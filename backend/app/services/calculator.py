from typing import Dict, Any

class TradingCalculator:
    """Calculator for Indian stock market charges and margins."""
    
    # Constants for Equity Intraday (approximate)
    BROKERAGE_MAX = 20.0  # Max brokerage per order
    BROKERAGE_PCT = 0.0003  # 0.03%
    STT_PCT = 0.00025  # 0.025% on sell side only
    EXCHANGE_TXN_PCT = 0.0000322  # NSE: 0.00322%
    GST_PCT = 0.18  # 18% on (Brokerage + Exchange Txn)
    SEBI_CHARGES_PCT = 0.000001  # ₹10 per crore (0.0001%)
    STAMP_DUTY_PCT = 0.00003  # 0.003% on buy side only
    
    @classmethod
    def calculate_equity_intraday(cls, symbol: str, quantity: int, price: float, side: str) -> Dict[str, Any]:
        """Calculate breakup for Equity Intraday trades."""
        trade_value = quantity * price
        
        # 1. Brokerage
        brokerage = min(cls.BROKERAGE_MAX, trade_value * cls.BROKERAGE_PCT)
        
        # 2. STT/CTT
        stt = trade_value * cls.STT_PCT if side.upper() == "SELL" else 0
        
        # 3. Transaction Charges
        txn_charges = trade_value * cls.EXCHANGE_TXN_PCT
        
        # 4. GST
        gst = (brokerage + txn_charges) * cls.GST_PCT
        
        # 5. SEBI Charges
        sebi_charges = trade_value * cls.SEBI_CHARGES_PCT
        
        # 6. Stamp Duty
        stamp_duty = trade_value * cls.STAMP_DUTY_PCT if side.upper() == "BUY" else 0
        
        total_tax_and_charges = brokerage + stt + txn_charges + gst + sebi_charges + stamp_duty
        net_value = trade_value - total_tax_and_charges if side.upper() == "SELL" else trade_value + total_tax_and_charges
        
        return {
            "symbol": symbol,
            "side": side.upper(),
            "quantity": quantity,
            "price": price,
            "trade_value": round(trade_value, 2),
            "breakup": {
                "brokerage": round(brokerage, 2),
                "stt": round(stt, 2),
                "exchange_txn": round(txn_charges, 2),
                "gst": round(gst, 2),
                "sebi_charges": round(sebi_charges, 2),
                "stamp_duty": round(stamp_duty, 2)
            },
            "total_charges": round(total_tax_and_charges, 2),
            "net_amount": round(net_value, 2),
            "required_margin": round(trade_value / 5, 2)  # Typically 5x leverage for intraday
        }

    @classmethod
    def calculate_options(cls, symbol: str, quantity: int, premium: float, side: str) -> Dict[str, Any]:
        """Calculate breakup for Options trades."""
        trade_value = quantity * premium
        
        # Options have fixed brokerage usually ₹20
        brokerage = 20.0
        
        # STT on Options is only on Sell side (0.0625% on premium)
        stt = trade_value * 0.000625 if side.upper() == "SELL" else 0
        
        # Transaction charges (NSE Options: 0.05% on premium)
        txn_charges = trade_value * 0.0005
        
        # GST (18% on Brokerage + Txn)
        gst = (brokerage + txn_charges) * cls.GST_PCT
        
        # SEBI
        sebi_charges = trade_value * cls.SEBI_CHARGES_PCT
        
        # Stamp Duty (0.003% on Buy side)
        stamp_duty = trade_value * 0.00003 if side.upper() == "BUY" else 0
        
        total_tax_and_charges = brokerage + stt + txn_charges + gst + sebi_charges + stamp_duty
        
        return {
            "symbol": symbol,
            "side": side.upper(),
            "quantity": quantity,
            "premium": premium,
            "trade_value": round(trade_value, 2),
            "breakup": {
                "brokerage": round(brokerage, 2),
                "stt": round(stt, 2),
                "exchange_txn": round(txn_charges, 2),
                "gst": round(gst, 2),
                "sebi_charges": round(sebi_charges, 2),
                "stamp_duty": round(stamp_duty, 2)
            },
            "total_charges": round(total_tax_and_charges, 2),
            "required_margin": round(trade_value, 2) # Options buy requires full premium
        }
