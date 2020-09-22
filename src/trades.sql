CREATE TABLE Trades (
    TradeID int,
    OrderType varchar(255),
    Symbol varchar(255),
    QTY varchar(255),
    MarketType varchar(255)
    Error varchar(255)
);

symbol=item.ticker,
            side=item.order,
            type='market',
            qty=item.contracts,
            time_in_force='day'
