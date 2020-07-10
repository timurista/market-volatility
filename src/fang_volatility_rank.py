# coding=utf8
import numpy as np

# import matplotlib.pyplot as plt
import yfinance as yf
import scipy.optimize as optimization
import pandas as pd
import datetime
import json

free_risk = 0.5
SMP_500_TICKER = "^GSPC"


def stock_data(start_date, end_date, ticker1, ticker2=SMP_500_TICKER):
    stock1 = yf.download(ticker1, start=start_date, end=end_date)

    start_date_s2 = datetime.datetime.now() - datetime.timedelta(days=10)
    end_date_s2 = datetime.datetime.now()
    stock2 = yf.download(ticker2, start=start_date, end=end_date)

    # use resampling to get stocks in more gaussian monthly returns
    r_stock1 = stock1.resample("M").last()
    r_stock2 = stock2.resample("M").last()

    # data frame
    data = pd.DataFrame(
        {"s_adjclose": r_stock1["Adj Close"], "m_adjclose": r_stock2["Adj Close"]},
        index=r_stock1.index,
    )

    # get the returns by taking log of the data
    data[["s_returns", "m_returns"]] = np.log(
        data[["s_adjclose", "m_adjclose"]] / data[["s_adjclose", "m_adjclose"]].shift(1)
    )

    data = data.dropna()

    return data


def get_covmat(data):
    # calc covariance
    covmat = np.cov(data["s_returns"], data["m_returns"])
    return covmat


def get_beta(covmat):
    # beta using formula
    beta = covmat[0, 1] / covmat[1, 1]
    return beta


def get_beta_r(data):
    # beta using formula
    beta_r = None
    try:
        beta_r, alpha = np.polyfit(data["m_returns"], data["s_returns"], deg=1)
    except Exception as e:
        print(e)
    return beta_r


def capm_beta(start_date, end_date, ticker1, ticker2=SMP_500_TICKER):
    data = stock_data(start_date, end_date, ticker1, ticker2)
    covmat = get_covmat(data)
    beta = get_beta(covmat)
    return beta


def capm_beta_r(start_date, end_date, ticker1, ticker2=SMP_500_TICKER):
    data = stock_data(start_date, end_date, ticker1, ticker2)
    beta_r = get_beta_r(data)
    return beta_r


# def capm(start_date, end_date, ticker1, ticker2=SMP_500_TICKER):
#     data = stock_data(start_date, end_date, ticker1, ticker2)
#     covmat = get_covmat(data)
#     beta = get_beta(covmat)

#     # linear regression
#     beta_r, alpha = np.polyfit(data["m_returns"], data["s_returns"], deg=1)
#     print(f"Beta from regresison: {beta_r}")

#     # fig, axis = plt.subplots(1, figsize=(20, 10))
#     axis.scatter(data["m_returns"], data["s_returns"], label="data returns")
#     axis.plot(
#         data["m_returns"],
#         beta_r * data["m_returns"] + alpha,
#         color="red",
#         label="CAPM line",
#     )
#     plt.title("CAPM, alphas and betas")
#     plt.xlabel("Market Return $R_m$", fontsize=18)
#     plt.ylabel("Stock Return $R_a$")
#     plt.text(0.08, 0.05, r"$R_a = \beta * R_m + \alpha$", fontsize=18)
#     plt.legend()
#     plt.grid(True)
#     plt.show()

#     # calc expected return
#     expected_return = free_risk + beta * (data["m_returns"].mean() * 12 - free_risk)
#     print("Expected return:", expected_return)


def get_expected_return(data, beta):
    return free_risk + beta * (data["m_returns"].mean() * 12 - free_risk)


def capm_expected_return(start_date, end_date, ticker1, ticker2=SMP_500_TICKER):
    data = stock_data(start_date, end_date, ticker1, ticker2)
    beta = get_beta_r(data)
    return get_expected_return(data, beta)

def write_fang_change():
    stocks = ["AAPL", "FB", "GOOGL", "NFLX", "MSFT", "NVDA"]
    start_date = datetime.datetime.now() - datetime.timedelta(days=10)
    # start_date = start_date
    end_date = datetime.datetime.now()
    stock_list = []
    for stock in stocks:
        beta_r = capm_beta_r(start_date, end_date, stock)
        if beta_r:
            stock_list.append({"ticker":stock, "volatility": beta_r })

        stock_list.sort(key=lambda x: x["volatility"], reverse=True)

    with open("fang_volatility.json", "w") as f:
        f.write(
            json.dumps(
                {"list": stock_list, "updated": datetime.datetime.now().isoformat()}, indent=2
            )
        )


if __name__ == "__main__":
    write_fang_change()