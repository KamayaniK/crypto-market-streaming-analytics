-- ============================================================
-- Crypto Market Streaming Analytics
-- SQL Views
-- ============================================================

-- 1. Latest market snapshot for each cryptocurrency
CREATE OR REPLACE VIEW latest_crypto_market AS
SELECT c.*
FROM crypto_market_data c
INNER JOIN (
    SELECT symbol, MAX(id) AS max_id
    FROM crypto_market_data
    GROUP BY symbol
) latest
ON c.symbol = latest.symbol
AND c.id = latest.max_id;


-- 2. Streaming analytics
-- Calculates change from the previous observation
-- and rolling price volatility.
CREATE OR REPLACE VIEW crypto_stream_analytics AS
SELECT
    id,
    timestamp,
    symbol,
    name,
    price_usd,
    market_cap_usd,
    volume_24h_usd,
    price_change_24h_pct,
    market_cap_rank,

    LAG(price_usd) OVER (
        PARTITION BY symbol
        ORDER BY id
    ) AS previous_price_usd,

    ROUND(
        (
            (price_usd -
             LAG(price_usd) OVER (
                 PARTITION BY symbol
                 ORDER BY id
             ))
            /
            NULLIF(
                LAG(price_usd) OVER (
                    PARTITION BY symbol
                    ORDER BY id
                ),
                0
            )
        ) * 100,
        4
    ) AS stream_price_change_pct,

    STDDEV_SAMP(price_usd) OVER (
        PARTITION BY symbol
        ORDER BY id
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS rolling_price_volatility

FROM crypto_market_data;


-- 3. Market signals
-- Flags significant price movements and volume spikes.
CREATE OR REPLACE VIEW crypto_market_signals AS
SELECT *,
    LAG(volume_24h_usd) OVER (
        PARTITION BY symbol
        ORDER BY id
    ) AS previous_volume_24h_usd,

    ROUND(
        (
            (volume_24h_usd -
             LAG(volume_24h_usd) OVER (
                 PARTITION BY symbol
                 ORDER BY id
             ))
            /
            NULLIF(
                LAG(volume_24h_usd) OVER (
                    PARTITION BY symbol
                    ORDER BY id
                ),
                0
            )
        ) * 100,
        4
    ) AS volume_change_pct,

    CASE
        WHEN ABS(stream_price_change_pct) >= 1
            THEN 'SIGNIFICANT_PRICE_MOVEMENT'

        WHEN ABS(
            (
                (volume_24h_usd -
                 LAG(volume_24h_usd) OVER (
                     PARTITION BY symbol
                     ORDER BY id
                 ))
                /
                NULLIF(
                    LAG(volume_24h_usd) OVER (
                        PARTITION BY symbol
                        ORDER BY id
                    ),
                    0
                )
            ) * 100
        ) >= 5
            THEN 'VOLUME_SPIKE'

        ELSE 'NORMAL'
    END AS market_signal

FROM crypto_stream_analytics;


-- 4. Dashboard summary
-- Provides the latest analytical record for each asset.
CREATE OR REPLACE VIEW dashboard_crypto_summary AS
SELECT
    symbol,
    name,
    price_usd,
    market_cap_usd,
    volume_24h_usd,
    price_change_24h_pct,
    market_cap_rank,
    stream_price_change_pct,
    rolling_price_volatility,
    previous_volume_24h_usd,
    volume_change_pct,
    market_signal,
    timestamp
FROM crypto_market_signals
WHERE id IN (
    SELECT MAX(id)
    FROM crypto_market_signals
    GROUP BY symbol
);


-- 5. 15-minute rolling/window analytics
-- Three observations correspond approximately to 15 minutes
-- because the producer collects data every 5 minutes.
CREATE OR REPLACE VIEW crypto_window_analytics AS
SELECT
    id,
    timestamp,
    symbol,
    name,
    price_usd,
    market_cap_usd,
    volume_24h_usd,
    price_change_24h_pct,

    AVG(price_usd) OVER (
        PARTITION BY symbol
        ORDER BY id
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS rolling_avg_price,

    MIN(price_usd) OVER (
        PARTITION BY symbol
        ORDER BY id
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS rolling_min_price,

    MAX(price_usd) OVER (
        PARTITION BY symbol
        ORDER BY id
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS rolling_max_price,

    STDDEV_SAMP(price_usd) OVER (
        PARTITION BY symbol
        ORDER BY id
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS rolling_price_stddev,

    COUNT(*) OVER (
        PARTITION BY symbol
        ORDER BY id
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS window_observations

FROM crypto_market_data;