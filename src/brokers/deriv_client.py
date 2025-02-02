"""
Deriv.com API connection handler
Handles authentication, order execution, and market data streaming

File Location: src/brokers/deriv_client.py
"""

import asyncio
from typing import Dict, Optional
from deriv_api import DerivAPI, APIError

class DerivTradingClient:
    """Main interface for Deriv.com API operations"""
    
    def __init__(self, app_id: str, token: str):
        """
        Initialize API connection parameters
        
        Args:
            app_id: Deriv application identifier
            token: API authentication token
        """
        self.api = DerivAPI(app_id=app_id)
        self.token = token
        self.account_info: Optional[Dict] = None

    async def connect(self) -> None:
        """Establish secure connection to Deriv API servers"""
        try:
            await self.api.authorize(self.token)
            self.account_info = await self.api.account_status()
        except APIError as e:
            self._handle_api_error(e, "connection")

    async def place_order(self, symbol: str, direction: str, 
                        amount: float, duration: int = 300) -> Dict:
        """
        Execute a contract purchase on Deriv platform
        
        Args:
            symbol: Financial instrument ID (e.g., 'R_100')
            direction: Trade direction (CALL/PUT)
            amount: Stake amount in USD
            duration: Contract duration in seconds
            
        Returns:
            Dictionary containing order details
            
        Raises:
            TradingException: On order placement failure
        """
        try:
            # Validate order parameters before execution
            if amount < 0.35:
                raise ValueError("Minimum stake is $0.35")
                
            contract = await self.api.buy_contract(
                contract_type=direction.upper(),
                currency="USD",
                symbol=symbol,
                amount=str(amount),
                duration_unit="s",
                duration=str(duration)
            )
            
            return self._parse_contract_response(contract)
            
        except APIError as e:
            self._handle_api_error(e, "order placement")
            return {}