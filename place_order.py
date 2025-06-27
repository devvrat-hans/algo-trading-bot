"""
Order Placement Module using Alpaca API
Handles buy/sell orders, position management, and risk controls
"""

import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
from typing import Optional, Dict, List, Union
import json

from config import (
    ALPACA_CONFIG, ORDER_CONFIG, RISK_MANAGEMENT, 
    POSITION_SIZING, ENVIRONMENT, DEFAULT_INSTRUMENT
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlpacaOrderManager:
    """
    Manages order placement and portfolio operations using Alpaca API
    """
    
    def __init__(self):
        """Initialize Alpaca API connection"""
        try:
            self.api = tradeapi.REST(
                ALPACA_CONFIG['api_key'],
                ALPACA_CONFIG['secret_key'],
                ALPACA_CONFIG['base_url'],
                api_version='v2'
            )
            
            # Verify connection
            account = self.api.get_account()
            logger.info(f"Connected to Alpaca API - Account Status: {account.status}")
            logger.info(f"Buying Power: ${float(account.buying_power):,.2f}")
            
            self.account = account
            self.is_connected = True
            
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca API: {e}")
            self.is_connected = False
            self.api = None
            self.account = None
    
    def get_account_info(self) -> Optional[Dict]:
        """Get current account information"""
        if not self.is_connected:
            return None
        
        try:
            account = self.api.get_account()
            account_info = {
                'account_id': account.id,
                'status': account.status,
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'equity': float(account.equity),
                'pattern_day_trader': getattr(account, 'pattern_day_trader', False)
            }
            
            # Add day_trade_count if available (might not be available in paper trading)
            if hasattr(account, 'day_trade_count'):
                account_info['day_trade_count'] = int(account.day_trade_count)
            else:
                account_info['day_trade_count'] = 0
                
            return account_info
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def get_positions(self) -> Optional[List[Dict]]:
        """Get current positions"""
        if not self.is_connected:
            return None
        
        try:
            positions = self.api.list_positions()
            position_list = []
            
            for position in positions:
                position_list.append({
                    'symbol': position.symbol,
                    'qty': float(position.qty),
                    'side': position.side,
                    'market_value': float(position.market_value),
                    'cost_basis': float(position.cost_basis),
                    'unrealized_pl': float(position.unrealized_pl),
                    'unrealized_plpc': float(position.unrealized_plpc),
                    'current_price': float(position.current_price)
                })
            
            return position_list
        
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return None
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get position for a specific symbol"""
        if not self.is_connected:
            return None
        
        try:
            position = self.api.get_position(symbol)
            return {
                'symbol': position.symbol,
                'qty': float(position.qty),
                'side': position.side,
                'market_value': float(position.market_value),
                'cost_basis': float(position.cost_basis),
                'unrealized_pl': float(position.unrealized_pl),
                'unrealized_plpc': float(position.unrealized_plpc),
                'current_price': float(position.current_price)
            }
        except Exception as e:
            logger.warning(f"No position found for {symbol} or error: {e}")
            return None
    
    def calculate_position_size(self, symbol: str, price: float, signal_strength: float = 1.0) -> float:
        """
        Calculate position size based on configured method
        
        Args:
            symbol: Trading symbol
            price: Current price
            signal_strength: Signal strength (0.0 to 1.0)
        
        Returns:
            Number of shares to trade
        """
        account_info = self.get_account_info()
        if not account_info:
            return 0
        
        method = POSITION_SIZING['method']
        max_position_value = min(
            RISK_MANAGEMENT['max_position_size'],
            account_info['buying_power'] * RISK_MANAGEMENT['max_portfolio_risk']
        )
        
        if method == 'fixed_amount':
            position_value = min(POSITION_SIZING['fixed_amount'], max_position_value)
        
        elif method == 'fixed_percentage':
            portfolio_value = account_info['portfolio_value']
            position_value = min(
                portfolio_value * POSITION_SIZING['fixed_percentage'],
                max_position_value
            )
        
        elif method == 'volatility_based':
            # Simplified volatility-based sizing
            # In practice, you'd calculate actual volatility
            base_amount = POSITION_SIZING['fixed_amount']
            volatility_adj = POSITION_SIZING['volatility_multiplier']
            position_value = min(base_amount * volatility_adj, max_position_value)
        
        else:
            position_value = POSITION_SIZING['fixed_amount']
        
        # Apply signal strength
        position_value *= signal_strength
        
        # Calculate shares
        shares = position_value / price
        
        # Round to appropriate precision
        if ORDER_CONFIG['fractional_shares']:
            shares = round(shares, 6)  # Up to 6 decimal places
        else:
            shares = int(shares)  # Whole shares only
        
        logger.info(f"Calculated position size for {symbol}: {shares} shares (${position_value:.2f})")
        return shares
    
    def place_market_order(self, symbol: str, qty: float, side: str, 
                          time_in_force: str = None, extended_hours: bool = None) -> Optional[Dict]:
        """
        Place a market order
        
        Args:
            symbol: Trading symbol
            qty: Quantity (positive number)
            side: 'buy' or 'sell'
            time_in_force: 'day', 'gtc', 'ioc', 'fok'
            extended_hours: Allow extended hours trading
        
        Returns:
            Order details or None if failed
        """
        if not self.is_connected:
            logger.error("Not connected to Alpaca API")
            return None
        
        if ENVIRONMENT['dry_run']:
            logger.info(f"DRY RUN: Would place {side} order for {qty} shares of {symbol}")
            return {'id': 'dry_run', 'status': 'simulated'}
        
        # Set defaults
        time_in_force = time_in_force or ORDER_CONFIG['default_time_in_force']
        extended_hours = extended_hours if extended_hours is not None else ORDER_CONFIG['extended_hours']
        
        try:
            # Validate order
            if qty <= 0:
                logger.error("Order quantity must be positive")
                return None
            
            if side not in ['buy', 'sell']:
                logger.error("Order side must be 'buy' or 'sell'")
                return None
            
            # Check if we have enough buying power (for buy orders)
            if side == 'buy':
                account_info = self.get_account_info()
                if account_info:
                    # Get current price for estimation
                    current_price = self.get_current_price(symbol)
                    if current_price:
                        estimated_cost = qty * current_price
                        if estimated_cost > account_info['buying_power']:
                            logger.error(f"Insufficient buying power. Need ${estimated_cost:.2f}, have ${account_info['buying_power']:.2f}")
                            return None
            
            # Place the order
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='market',
                time_in_force=time_in_force,
                extended_hours=extended_hours
            )
            
            order_details = {
                'id': order.id,
                'symbol': order.symbol,
                'qty': float(order.qty),
                'side': order.side,
                'order_type': order.order_type,
                'time_in_force': order.time_in_force,
                'status': order.status,
                'submitted_at': order.submitted_at,
                'extended_hours': extended_hours
            }
            
            logger.info(f"Order placed successfully: {order.id}")
            logger.info(f"  Symbol: {symbol}")
            logger.info(f"  Side: {side.upper()}")
            logger.info(f"  Quantity: {qty}")
            logger.info(f"  Status: {order.status}")
            
            return order_details
            
        except Exception as e:
            logger.error(f"Error placing market order: {e}")
            return None
    
    def place_limit_order(self, symbol: str, qty: float, side: str, limit_price: float,
                         time_in_force: str = None, extended_hours: bool = None) -> Optional[Dict]:
        """
        Place a limit order
        
        Args:
            symbol: Trading symbol
            qty: Quantity
            side: 'buy' or 'sell'
            limit_price: Limit price
            time_in_force: Order duration
            extended_hours: Extended hours trading
        
        Returns:
            Order details or None if failed
        """
        if not self.is_connected:
            logger.error("Not connected to Alpaca API")
            return None
        
        if ENVIRONMENT['dry_run']:
            logger.info(f"DRY RUN: Would place {side} limit order for {qty} shares of {symbol} at ${limit_price}")
            return {'id': 'dry_run_limit', 'status': 'simulated'}
        
        time_in_force = time_in_force or ORDER_CONFIG['default_time_in_force']
        extended_hours = extended_hours if extended_hours is not None else ORDER_CONFIG['extended_hours']
        
        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='limit',
                limit_price=limit_price,
                time_in_force=time_in_force,
                extended_hours=extended_hours
            )
            
            order_details = {
                'id': order.id,
                'symbol': order.symbol,
                'qty': float(order.qty),
                'side': order.side,
                'order_type': order.order_type,
                'limit_price': float(order.limit_price),
                'time_in_force': order.time_in_force,
                'status': order.status,
                'submitted_at': order.submitted_at
            }
            
            logger.info(f"Limit order placed: {order.id} - {side.upper()} {qty} {symbol} @ ${limit_price}")
            return order_details
            
        except Exception as e:
            logger.error(f"Error placing limit order: {e}")
            return None
    
    def place_stop_loss_order(self, symbol: str, qty: float, stop_price: float,
                             limit_price: float = None) -> Optional[Dict]:
        """
        Place a stop-loss order
        
        Args:
            symbol: Trading symbol
            qty: Quantity (positive for sell, negative for buy stop)
            stop_price: Stop trigger price
            limit_price: Limit price (for stop-limit orders)
        
        Returns:
            Order details or None if failed
        """
        if not self.is_connected:
            return None
        
        if ENVIRONMENT['dry_run']:
            order_type = 'stop_limit' if limit_price else 'stop'
            logger.info(f"DRY RUN: Would place {order_type} order for {qty} shares of {symbol} at stop ${stop_price}")
            return {'id': 'dry_run_stop', 'status': 'simulated'}
        
        try:
            # Determine order type and side
            side = 'sell' if qty > 0 else 'buy'
            qty = abs(qty)
            
            if limit_price:
                # Stop-limit order
                order = self.api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side=side,
                    type='stop_limit',
                    stop_price=stop_price,
                    limit_price=limit_price,
                    time_in_force='gtc'  # Good till canceled for stop orders
                )
            else:
                # Stop order
                order = self.api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side=side,
                    type='stop',
                    stop_price=stop_price,
                    time_in_force='gtc'
                )
            
            order_details = {
                'id': order.id,
                'symbol': order.symbol,
                'qty': float(order.qty),
                'side': order.side,
                'order_type': order.order_type,
                'stop_price': float(order.stop_price),
                'status': order.status,
                'submitted_at': order.submitted_at
            }
            
            if limit_price:
                order_details['limit_price'] = float(order.limit_price)
            
            logger.info(f"Stop-loss order placed: {order.id}")
            return order_details
            
        except Exception as e:
            logger.error(f"Error placing stop-loss order: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        if not self.is_connected:
            return False
        
        try:
            self.api.cancel_order(order_id)
            logger.info(f"Order {order_id} cancelled successfully")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    def get_orders(self, status: str = 'all', limit: int = 50) -> Optional[List[Dict]]:
        """Get orders with specified status"""
        if not self.is_connected:
            return None
        
        try:
            orders = self.api.list_orders(status=status, limit=limit)
            order_list = []
            
            for order in orders:
                order_dict = {
                    'id': order.id,
                    'symbol': order.symbol,
                    'qty': float(order.qty),
                    'filled_qty': float(order.filled_qty or 0),
                    'side': order.side,
                    'order_type': order.order_type,
                    'status': order.status,
                    'submitted_at': order.submitted_at,
                    'time_in_force': order.time_in_force
                }
                
                # Add price fields if they exist
                if hasattr(order, 'limit_price') and order.limit_price:
                    order_dict['limit_price'] = float(order.limit_price)
                if hasattr(order, 'stop_price') and order.stop_price:
                    order_dict['stop_price'] = float(order.stop_price)
                if hasattr(order, 'filled_avg_price') and order.filled_avg_price:
                    order_dict['filled_avg_price'] = float(order.filled_avg_price)
                
                order_list.append(order_dict)
            
            return order_list
        
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        if not self.is_connected:
            return None
        
        try:
            # Try to get latest trade
            trades = self.api.get_latest_trade(symbol)
            if trades and hasattr(trades, 'price'):
                return float(trades.price)
            
            # Fallback to snapshot
            snapshot = self.api.get_snapshot(symbol)
            if snapshot and snapshot.latest_trade:
                return float(snapshot.latest_trade.price)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None
    
    def close_position(self, symbol: str, percentage: float = 100.0) -> Optional[Dict]:
        """
        Close a position (partial or full)
        
        Args:
            symbol: Symbol to close
            percentage: Percentage of position to close (default: 100%)
        
        Returns:
            Order details or None if failed
        """
        position = self.get_position(symbol)
        if not position:
            logger.warning(f"No position found for {symbol}")
            return None
        
        # Calculate quantity to close
        current_qty = abs(float(position['qty']))
        qty_to_close = current_qty * (percentage / 100.0)
        
        if ORDER_CONFIG['fractional_shares']:
            qty_to_close = round(qty_to_close, 6)
        else:
            qty_to_close = int(qty_to_close)
        
        # Determine side (opposite of current position)
        side = 'sell' if float(position['qty']) > 0 else 'buy'
        
        logger.info(f"Closing {percentage}% of {symbol} position: {side} {qty_to_close} shares")
        
        return self.place_market_order(symbol, qty_to_close, side)
    
    def implement_risk_management(self, symbol: str, entry_price: float, 
                                 position_qty: float) -> Dict[str, Optional[str]]:
        """
        Implement stop-loss and take-profit orders
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price of the position
            position_qty: Position quantity (positive for long, negative for short)
        
        Returns:
            Dictionary with stop_loss_order_id and take_profit_order_id
        """
        if not self.is_connected:
            return {'stop_loss_order_id': None, 'take_profit_order_id': None}
        
        is_long = position_qty > 0
        abs_qty = abs(position_qty)
        
        # Calculate stop-loss price
        if is_long:
            stop_loss_price = round(entry_price * (1 - RISK_MANAGEMENT['stop_loss_pct']), 2)
            take_profit_price = round(entry_price * (1 + RISK_MANAGEMENT['take_profit_pct']), 2)
        else:
            stop_loss_price = round(entry_price * (1 + RISK_MANAGEMENT['stop_loss_pct']), 2)
            take_profit_price = round(entry_price * (1 - RISK_MANAGEMENT['take_profit_pct']), 2)
        
        result = {'stop_loss_order_id': None, 'take_profit_order_id': None}
        
        # Place stop-loss order
        try:
            stop_qty = abs_qty if is_long else -abs_qty
            stop_order = self.place_stop_loss_order(symbol, stop_qty, stop_loss_price)
            if stop_order:
                result['stop_loss_order_id'] = stop_order['id']
                logger.info(f"Stop-loss placed at ${stop_loss_price:.2f}")
        except Exception as e:
            logger.error(f"Failed to place stop-loss: {e}")
        
        # Place take-profit order (limit order)
        try:
            tp_side = 'sell' if is_long else 'buy'
            tp_order = self.place_limit_order(symbol, abs_qty, tp_side, take_profit_price, 'gtc')
            if tp_order:
                result['take_profit_order_id'] = tp_order['id']
                logger.info(f"Take-profit placed at ${take_profit_price:.2f}")
        except Exception as e:
            logger.error(f"Failed to place take-profit: {e}")
        
        return result
    
    def execute_signal(self, symbol: str, signal: int, current_price: float = None, 
                      signal_strength: float = 1.0) -> Optional[Dict]:
        """
        Execute a trading signal
        
        Args:
            symbol: Trading symbol
            signal: 1 for buy, -1 for sell, 0 for hold
            current_price: Current price (will fetch if not provided)
            signal_strength: Signal strength (0.0 to 1.0)
        
        Returns:
            Execution results
        """
        if signal == 0:
            logger.info(f"Hold signal for {symbol} - no action taken")
            return None
        
        if current_price is None:
            current_price = self.get_current_price(symbol)
            if current_price is None:
                logger.error(f"Could not get current price for {symbol}")
                return None
        
        # Check existing position
        existing_position = self.get_position(symbol)
        current_qty = float(existing_position['qty']) if existing_position else 0.0
        
        logger.info(f"Executing signal for {symbol}: {signal} (strength: {signal_strength})")
        logger.info(f"Current price: ${current_price:.2f}")
        logger.info(f"Current position: {current_qty} shares")
        
        execution_result = {
            'symbol': symbol,
            'signal': signal,
            'current_price': current_price,
            'signal_strength': signal_strength,
            'orders': [],
            'risk_management': {}
        }
        
        if signal == 1:  # Buy signal
            if current_qty < 0:
                # Close short position first
                close_order = self.close_position(symbol)
                if close_order:
                    execution_result['orders'].append(close_order)
                    logger.info("Closed short position")
            
            # Calculate position size
            qty = self.calculate_position_size(symbol, current_price, signal_strength)
            if qty > 0:
                # Place buy order
                buy_order = self.place_market_order(symbol, qty, 'buy')
                if buy_order:
                    execution_result['orders'].append(buy_order)
                    
                    # Implement risk management
                    risk_orders = self.implement_risk_management(symbol, current_price, qty)
                    execution_result['risk_management'] = risk_orders
        
        elif signal == -1:  # Sell signal
            if current_qty > 0:
                # Close long position
                close_order = self.close_position(symbol)
                if close_order:
                    execution_result['orders'].append(close_order)
                    logger.info("Closed long position")
            
            # For short selling (if account supports it)
            if hasattr(self.account, 'shorting_enabled') and self.account.shorting_enabled:
                qty = self.calculate_position_size(symbol, current_price, signal_strength)
                if qty > 0:
                    sell_order = self.place_market_order(symbol, qty, 'sell')
                    if sell_order:
                        execution_result['orders'].append(sell_order)
                        
                        # Implement risk management for short position
                        risk_orders = self.implement_risk_management(symbol, current_price, -qty)
                        execution_result['risk_management'] = risk_orders
        
        return execution_result

def main():
    """Demo and test the order management system"""
    print("Alpaca Order Manager Demo")
    print("=" * 50)
    
    # Initialize order manager
    order_manager = AlpacaOrderManager()
    
    if not order_manager.is_connected:
        print("❌ Failed to connect to Alpaca API")
        print("Please check your API credentials and configuration")
        return
    
    print("✅ Connected to Alpaca API")
    
    # Get account info
    account_info = order_manager.get_account_info()
    if account_info:
        print(f"\n📊 Account Information:")
        print(f"  Status: {account_info['status']}")
        print(f"  Buying Power: ${account_info['buying_power']:,.2f}")
        print(f"  Portfolio Value: ${account_info['portfolio_value']:,.2f}")
        print(f"  Cash: ${account_info['cash']:,.2f}")
    
    # Get positions
    positions = order_manager.get_positions()
    if positions:
        print(f"\n📈 Current Positions ({len(positions)}):")
        for pos in positions:
            print(f"  {pos['symbol']}: {pos['qty']} shares @ ${pos['current_price']:.2f}")
            print(f"    Market Value: ${pos['market_value']:,.2f}")
            print(f"    P&L: ${pos['unrealized_pl']:,.2f} ({pos['unrealized_plpc']:.2%})")
    else:
        print("\n📈 No current positions")
    
    # Get recent orders
    orders = order_manager.get_orders(status='all', limit=5)
    if orders:
        print(f"\n📋 Recent Orders ({len(orders)}):")
        for order in orders:
            print(f"  {order['symbol']}: {order['side'].upper()} {order['qty']} @ {order['order_type']}")
            print(f"    Status: {order['status']} | Submitted: {order['submitted_at']}")
    
    # Demo signal execution (dry run)
    print(f"\n🎯 Demo Signal Execution (Dry Run):")
    test_symbol = DEFAULT_INSTRUMENT
    current_price = order_manager.get_current_price(test_symbol)
    
    if current_price:
        print(f"Current price of {test_symbol}: ${current_price:.2f}")
        
        # Simulate buy signal
        print(f"\n🟢 Simulating BUY signal for {test_symbol}")
        result = order_manager.execute_signal(test_symbol, 1, current_price, 0.8)
        if result:
            print(f"Signal executed: {len(result['orders'])} orders placed")
        
        # Show what position size would be calculated
        pos_size = order_manager.calculate_position_size(test_symbol, current_price, 1.0)
        print(f"Calculated position size: {pos_size} shares (${pos_size * current_price:.2f})")

if __name__ == "__main__":
    main()
