# HyperTrade Simulator

A module providing core classes and services for simulating trading strategies.

## Event-Driven Architecture

HyperTrade uses an event-driven design, where each component subscribes to and
processes specific events (e.g., order fulfillment, market price changes) as
they occur. This approach allows the simulation engine, portfolio manager,
performance tracker, and other services to communicate through an event
publishing and subscribing model, promoting modularity and flexibility.

## Main Components

- **engine.py**: Entry point that orchestrates event management, portfolio
  tracking, order execution, and market data.
- **event.py**: Defines the event system handling time progression and event
  publishing.
- **market.py**: Manages market events, generating price change updates for
  subscribed services.
- **assets.py**: Provides data structures representing tradeable assets.
- **strategy.py**: Supplies tools to build and execute trading strategies, tying
  into the event system.
- **financials**: Handles portfolios, performance tracking, and financial
  metrics.
- **execute**: Offers broker- and commission-related functionality.

Use these modules as a foundation for backtesting and running simulations within
HyperTrade.
