# Insight Engine - AI Trading & Options Chain POA

**Date:** 2026-04-21
**Status:** Implementation Phase

## User Requirements Summary

### AI Integration (Ollama)
- **Model**: Light 1.5B parameter model for ultra-fast coder-grade responses
- **Recommended**: `qwen2.5-coder:1.5b`
- **Endpoint**: localhost:11434 (standard Ollama)
- **Purpose**: Stock summary reports, target/SL recommendations

### Features to Implement

#### 1. AI Summary Page (`/ai-summary`)
- Stock-by-stock AI analysis for user holdings
- Target 1, 2, 3 and Stop Loss recommendations
- On-demand AI reports per share
- Fast chat-style responses

#### 2. Robo Call Trading Tab (`/trading`)
- Order placement interface with quantity selection
- Order breakdown showing:
  - Available balance
  - Trade charges calculation (Zerodha-style: ₹20/order)
  - Final amount for buy orders
  - Net receivable for sell orders (after charges)
- Quantity selector (min: 1, max: based on available balance)
- If balance low → prompt to add funds

#### 3. Options Chain Page (`/options`)
- Three separate tabs/pages:
  - Nifty 50 Options
  - Bank Nifty Options
  - Fin Nifty Options
- Real-time market data from Angel One SmartAPI
- Live charts
- Option chain with Call/Put suggestions
- Each suggestion shows:
  - LTP (Last Traded Price)
  - Strike Price
  - Stop Loss
  - Target
- Place order button for suggested calls
- Quantity selection with balance check
- Minimum quantity default, max based on available funds

#### 4. Historical Trade Ledger (`/ledger`)
- Past transactions from demat
- Fetch historical trade data
- Complete transaction history

## Technical Architecture Decisions

### Frontend Routes (to add in App.tsx)
```
/ai-summary    -> AISummaryPage
/trading       -> TradingPage
/options       -> OptionsChainPage
/ledger        -> TradeLedgerPage
```

### Backend APIs Needed
```
POST   /api/ai/analyze-stock       -> Get AI analysis for a stock
POST   /api/ai/analyze-holdings    -> Bulk analysis for all holdings
GET    /api/market/options-chain   -> Get options chain for index
POST   /api/orders/simulate       -> Simulate order and get breakdown
POST   /api/orders/place          -> Place actual order
GET    /api/ledger/history        -> Get historical trades
```

### Ollama Integration
- Model: `qwen2.5-coder:1.5b` (1.5B, optimized)
- Fallback: `qwen2.5-coder:1.5b` (Consistency)
- System prompt for trading analysis
- Streaming responses for chat-like feel

### Database Models Needed
- `AIAnalysis` - Store AI generated reports
- `SimulatedOrder` - Track paper/simulated trades
- `OptionsSuggestion` - Store generated suggestions

## Implementation Priority
1. AI Summary Page + Ollama integration
2. Trading Tab with order calculator
3. Options Chain with live data
4. Historical Ledger

## Notes
- Use existing broker factory for live data
- Maintain dark UI theme (slate-950)
- Follow existing patterns (HoldingsPage.tsx as reference)
- All features behind ProtectedRoute
