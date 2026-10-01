\# Real-Time Cryptocurrency Market Intelligence \& Streaming Analytics



\## 1. Project Overview



This project is a real-time cryptocurrency market monitoring and streaming analytics system.



It continuously collects live cryptocurrency market data from the CoinGecko API for five cryptocurrencies:



\- Bitcoin (BTC)

\- Ethereum (ETH)

\- Solana (SOL)

\- XRP (XRP)

\- Dogecoin (DOGE)



The data is streamed through Apache Kafka, consumed by a Python consumer, stored in MySQL, analyzed using SQL window functions, and visualized through Grafana.



The system also generates alerts for significant price movements and unusual trading-volume changes.



\---



\## 2. Business Problem



Cryptocurrency markets change continuously, making periodic or batch-based analysis insufficient for timely monitoring.



The purpose of this project is to demonstrate how continuously arriving market data can be processed in a streaming pipeline to identify meaningful changes and unusual activity.



The system helps a market analyst monitor multiple cryptocurrencies, identify significant price movements and volume spikes, and investigate market conditions through an interactive dashboard.



The project is designed for monitoring and decision support. It does not provide investment or buy/sell recommendations.



\---



\## 3. Architecture



```text

CoinGecko Live API

&#x20;       |

&#x20;       v

Python API Collector

&#x20;       |

&#x20;       v

Kafka Producer

&#x20;       |

&#x20;       v

Apache Kafka

Topic: crypto-market-data

&#x20;       |

&#x20;       v

Python Kafka Consumer

&#x20;       |

&#x20;       v

MySQL

Database: crypto\_analytics

&#x20;       |

&#x20;       v

SQL Streaming \& Window Analytics

&#x20;       |

&#x20;       v

Grafana

&#x20;       |

&#x20;       +--> Interactive Dashboard

&#x20;       |

&#x20;       +--> Market Alerts

