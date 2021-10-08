import pandas as pd
import numpy as np
from random import randint
from datetime import date
from api.dataAnalysing import topSources
from api.dataCleaning import extractSpecialWords, getTime


def getCustomizedData(data):
    return selectFiType(data, str(data['type'].upper()))


def getTransactions(transactions):
    print("Transactions")
    list_of_transactions = list(transactions)
    df = pd.DataFrame(list_of_transactions)
    return df


def selectFiType(data, fi_type):
    select_type = {
        "DEPOSIT": DEPOSIT,
        "TERM_DEPOSIT": TERM_DEPOSIT,
        "RECURRING_DEPOSIT": RECURRING_DEPOSIT,
        "CREDIT_CARD": CREDIT_CARD,
        "CD": CD,
        "SIP": SIP,
        "CP": CP,
        "GOVT_SECURITIES": GOVT_SECURITIES,
        "EQUITIES": EQUITIES,
        "BONDS": BONDS,
        "DEBENTURES": DEBENTURES,
        "MUTUAL_FUNDS": MUTUAL_FUNDS,
        "ETF": ETF,
        "EPF": EPF,
        "PPF": PPF,
        "IDR": IDR,
        "CIS": CIS,
        "AIF": AIF,
        "INSURANCE_POLICIES": INSURANCE_POLICIES,
        "ULIP": ULIP,
        "NPS": NPS,
        "INVIT": INVIT,
        "REIT": REIT
    }
    func = select_type.get(fi_type)
    return func(data)


def RECURRING_DEPOSIT(data):
    # df = getTransactions(data['transactions']['transaction'])
    # return df
    return data


def CD(data):
    # df = getTransactions(data['transactions']['transaction'])
    # return df
    return data


def CP(data):
    # df = getTransactions(data['transactions']['transaction'])
    # return df
    return data


def GOVT_SECURITIES(data):
    # df = getTransactions(data['transactions']['transaction'])
    # return df
    return data


def DEBENTURES(data):
    # df = getTransactions(data['transactions']['transaction'])
    # return df
    return data


def ETF(data):
    # df = getTransactions(data['transactions']['transaction'])
    # return df
    return data


def IDR(data):
    # df = getTransactions(data['transactions']['transaction'])
    # return df
    return data


def CIS(data):
    # df = getTransactions(data['transactions']['transaction'])
    # return df
    return data


def AIF(data):
    # df = getTransactions(data['transactions']['transaction'])
    # return df
    return data


def ULIP(data):
    # df = getTransactions(data['transactions']['transaction'])
    # return df
    return data


def NPS(data):
    # df = getTransactions(data['transactions']['transaction'])
    # return df
    return data


def INVIT(data):
    # df = getTransactions(data['transactions']['transaction'])
    # return df
    return data


def REIT(data):
    # df = getTransactions(data['transactions']['transaction'])
    # return df
    return data


# Deposits
def DEPOSIT(data):
    # Check for transactions Object present or not
    records = None
    top_sources = None
    credit_vs_debit = None
    cd_max_min_ratio = None
    top3_hourRange = None
    profile = None
    summary = None
    score = 100
    if data['profile'] is not None:
        profile = data['profile']['holders']
    if data['summary'] is not None:
        summary = data['summary']
    if data['transactions'] is not None:
        df = getTransactions(data['transactions']['transaction'])
        df['transactionTimestamp'] = pd.to_datetime(df['transactionTimestamp'])
        df['transactionTimestamp'] = df['transactionTimestamp'].dt.tz_localize(None)
        df['currentBalance'] = pd.to_numeric(df['currentBalance'])
        df['amount'] = pd.to_numeric(df['amount'])
        df = df[['mode', 'type', 'amount', 'narration', 'currentBalance', 'transactionTimestamp']]
        df['narration'] = df['narration'].map(extractSpecialWords)
        records = df.T.to_dict().values()
        # Top Sources
        narrations = list(df['narration'])
        top_sources = topSources(narrations=narrations)
        c_d = df.groupby(["type"]).size().reset_index()
        c_d["percentage"] = (c_d[0] / c_d[0].sum()) * 100
        c_d["percentage"] = c_d["percentage"].round(decimals=2)
        c_d.drop(columns=[0], axis=1, inplace=True)
        credit_vs_debit = dict(zip(c_d['type'], c_d['percentage']))
        max_idx = df.groupby(['type'])['amount'].transform(max) == df['amount']
        max_infer = df[max_idx].sort_values('transactionTimestamp').groupby('type').tail(1)
        max_infer['txn_date'] = max_infer['transactionTimestamp'].dt.date
        min_idx = df.groupby(['type'])['amount'].transform(min) == df['amount']
        df[min_idx].sort_values('transactionTimestamp').groupby('type').tail(1)
        min_infer = df[min_idx].sort_values('transactionTimestamp').groupby('type').tail(1)
        min_infer['txn_date'] = min_infer['transactionTimestamp'].dt.date
        cd_max_min_ratio = {
            "max": {
                "credit": dict(max_infer.loc[max_infer['type'] == "CREDIT"].iloc[0]),
                "debit": dict(max_infer.loc[max_infer['type'] == "DEBIT"].iloc[0])
            },
            "min": {
                "credit": dict(min_infer.loc[min_infer['type'] == "CREDIT"].iloc[0]),
                "debit": dict(min_infer.loc[min_infer['type'] == "DEBIT"].iloc[0])
            }
        }
        df['hour'] = df['transactionTimestamp'].dt.hour
        period = df.groupby(['type', 'hour']).size().reset_index(name='count')
        period = period.sort_values('count', ascending=False).groupby('type').head(3)
        top3_hourRange = {
            "credit": dict(
                zip(period.loc[period['type'] == "CREDIT"]['hour'], period.loc[period['type'] == "CREDIT"]['count'])),
            "debit": dict(
                zip(period.loc[period['type'] == "DEBIT"]['hour'], period.loc[period['type'] == "DEBIT"]['count']))
        }
        score = int((100 - abs(credit_vs_debit["CREDIT"] - credit_vs_debit["DEBIT"])) * 10)
    return construct_deposits(
        str(data['type']).upper(),
        profile=profile,
        summary=summary,
        records=list(records),
        top_sources=top_sources,
        cd=credit_vs_debit,
        ratio=cd_max_min_ratio,
        hour_range=top3_hourRange,
        score=round(score, 2))


def construct_deposits(fi_type, profile, summary, records, top_sources, cd, ratio, hour_range, score):
    return {
        "type": fi_type,
        "profile": profile,
        "summary": summary,
        "records": records,
        "insights": {
            "topSources": top_sources,
            "creditVsDebit": cd,
            "creditMinMaxRatio": ratio,
            "peekHourCount": hour_range
        },
        "wealthScore":  int(score if score > 100 else 100)
    }


def MUTUAL_FUNDS(data):
    records = None
    types_of_investment = None
    sources_of_investment = None
    profile = None
    summary = None
    investedValue = 0
    currentValue = 0
    dataStory = ''
    profit = 10
    days = 0
    if data['profile'] is not None:
        profile = data['profile']['holders']['holder']
    if data['summary'] is not None:
        summary = data['summary']
        investedValue = int(float(summary['investmentValue']))
        currentValue = int(float(summary['currentValue']))
        profit = ((currentValue - investedValue) / investedValue) * 100

    if data['transactions'] is not None:
        df = getTransactions(data['transactions']['transaction'])
        str_time = getTime(data['transactions']['startDate'])
        end_time = getTime(data['transactions']['endDate'])
        if str_time is not None and end_time is not None:
            days = (end_time - str_time).days
        elif str_time is not None:
            days = date.today() - str_time
        else:
            days = "X"

        df = df[['amc', 'mode', 'type', 'fundType', 'schemePlan', 'schemeCategory', 'executionDate']]
        total = len(df)
        df = df.assign(BuyAmount=getMockAmounts(investedValue, total))
        df = df.assign(CurrentAmount=getMockAmounts(currentValue, total))
        df['profit_loss'] = round(((df['CurrentAmount'] - df['BuyAmount']) / df['BuyAmount']) * 100, 2)
        records = df.T.to_dict().values()
        sources_of_investment = df['amc'].unique()
        types_of_investment = df['mode'].unique()

    if data['summary'] is not None and data['transactions'] is not None:
        dataStory = dataStory + "You have invested total of " + str(investedValue) + " in mutual funds "
        dataStory = dataStory + "After " + str(days) + " days it has become " + str(currentValue) + " and you are in"
        if profit > 0:
            dataStory = dataStory + " profit of " + str(profit) + "%"
        else:
            dataStory = dataStory + "Loss of " + str(profit) + "%"

    # return df
    return construct_mutual_funds(str(data['type']).upper(), dataStory, profile, summary, sources_of_investment,
                                  types_of_investment, records, profit)


def getMockAmounts(value, n):
    pieces = []
    for idx in range(n - 1):
        pieces.append(randint(1, value - sum(pieces) - n + idx))
    pieces.append(value - sum(pieces))
    return pieces


def construct_mutual_funds(fi_type, data_story, profile, summary,
                           sources_of_investment, types_of_investment, records, profit):
    return {
        "type": fi_type,
        "dataStory": data_story,
        "profile": profile,
        "summary": summary,
        "records": list(records),
        "insights": {
            "sourceOfInvestment": list(sources_of_investment),
            "typesOfInvestment": list(types_of_investment),
            "profit": profit
        },
        "wealthScore": int(round(profit, 2) * 10 if round(profit, 2) * 10 > 100 else 100)
    }


def BONDS(data):
    records = None
    currencies = None
    creditStatus = None
    profile = None
    summary = None
    investedValue = 0
    currentValue = 0
    dataStory = ''
    profit = 0
    days = 0
    score = 100
    if data['profile'] is not None:
        profile = data['profile']['holders']['holder']
    if data['summary'] is not None:
        summary = data['summary']
        investedValue = int(float(summary['investmentValue']))
        currentValue = int(float(summary['currentValue']))
        profit = ((currentValue - investedValue) / investedValue) * 100
        score = profit * 10
        creditRating = int(summary['holdings']['holding']['creditRating'])
        if creditRating < 500:
            creditStatus = "Low return bonds"
        elif 500 < creditRating < 650:
            creditStatus = "Average return bonds"
        elif 650 < creditRating < 740:
            creditStatus = "Good Return bonds"
        elif 740 < creditRating < 800:
            creditStatus = "Very Good Return bonds"
        else:
            creditStatus = "Best and Excellent Return bonds"

    if data['transactions'] is not None:
        df = getTransactions(data['transactions']['transaction'])
        records = df.T.to_dict().values()
        currencies = df['currency'].unique()

    if data['summary'] is not None and data['transactions'] is not None:
        dataStory = dataStory + "You have invested total of " + str(investedValue) + " in mutual funds "
        dataStory = dataStory + "After " + str(days) + " days it has become " + str(currentValue) + " and you are in"
        if profit > 0:
            dataStory = dataStory + " profit of " + str(profit) + "%"
        else:
            dataStory = dataStory + "Loss of " + str(profit) + "%"

    # return df
    return construct_bonds(str(data['type']).upper(), dataStory, profile,
                           summary, records, creditStatus, currencies, profit, score)


def construct_bonds(fi_type, data_story, profile, summary, records, credit_status, currencies, profit, score):
    return {
        "type": fi_type,
        "dataStory": data_story,
        "profile": profile,
        "summary": summary,
        "records": list(records),
        "insights": {
            "creditStatus": credit_status,
            "investedCurrencies": list(currencies),
            "profit": profit
        },
        "wealthScore": int(score if score > 100 else 100)
    }


def PPF(data):
    records = None
    top_sources = None
    top3_hourRange = None
    profile = None
    summary = None
    score = 100
    days = None
    if data['profile'] is not None:
        profile = data['profile']['holders']
    if data['summary'] is not None:
        summary = data['summary']
    if data['transactions'] is not None:
        df = getTransactions(data['transactions']['transaction'])
        str_time = getTime(data['transactions']['startDate'])
        end_time = getTime(data['transactions']['endDate'])
        df['txnDate'] = pd.to_datetime(df['txnDate'])
        df['txnDate'] = df['txnDate'].dt.tz_localize(None)
        if str_time is not None and end_time is not None:
            days = (end_time - str_time).days
        elif str_time is not None:
            days = date.today() - str_time
        else:
            days = "X"
        df['txnDate'] = pd.to_datetime(df['txnDate'])
        df['txnDate'] = df['txnDate'].dt.tz_localize(None)
        df['balance'] = pd.to_numeric(df['balance'])
        df['amount'] = pd.to_numeric(df['amount'])
        df = df[['type', 'amount', 'narration', 'balance', 'txnDate']]
        df['narration'] = df['narration'].map(extractSpecialWords)
        df['aggregateSum'] = df['balance'].cumsum()
        df['aggregateAmount'] = df['amount'].cumsum()
        total = len(df)
        records = df.T.to_dict().values()
        narrations = list(df['narration'])
        top_sources = topSources(narrations=narrations)
        df['hour'] = df['txnDate'].dt.hour
        period = df.groupby(['type', 'hour']).size().reset_index(name='count')
        period = period.sort_values('count', ascending=False).groupby('type').head(3)
        top3_hourRange = {
            "DEPOSIT": dict(
                zip(period.loc[period['type'] == "DEPOSIT"]['hour'], period.loc[period['type'] == "DEPOSIT"]['count'])),
        }
        if type(days) is not str:
            score = ((total - np.floor(days / 30)) / total) * 1000

    return construct_ppf(
        str(data['type']).upper(),
        profile=profile,
        summary=summary,
        records=list(records),
        top_sources=top_sources,
        frequent_deposits_hour=top3_hourRange,
        score=score
    )


def construct_ppf(fi_type, profile, summary, records, top_sources, frequent_deposits_hour, score):
    return {
        "type": fi_type,
        "profile": profile,
        "summary": summary,
        "records": records,
        "insights": {
            "topSources": top_sources,
            "frequent_deposits_hour": frequent_deposits_hour
        },
        "wealthScore": int(score if score > 100 else 100)
    }


def EPF(data):
    records = None
    top_sources = None
    next_25_years_estimation = None
    profile = None
    summary = None
    score = 100
    if data['profile'] is not None:
        profile = data['profile']['holders']['holder']
    if data['summary'] is not None:
        summary = data['summary']
    if data['transactions'] is not None:
        df = getTransactions(data['transactions']['transaction'])
        df['txnDate'] = pd.to_datetime(df['txnDate'])
        df['txnDate'] = df['txnDate'].dt.tz_localize(None)
        df['employeeDepositAmount'] = pd.to_numeric(df['employeeDepositAmount'])
        df['employeeWithdrawalAmount'] = pd.to_numeric(df['employeeWithdrawalAmount'])
        df['employerDepositAmount'] = df['employeeDepositAmount']
        df['narration'] = df['narration'].map(extractSpecialWords)
        df['employerPensionContribution'] = np.round(
            np.where(df['employeeDepositAmount'] > 3600, 1250, df['employeeDepositAmount'] * 64 / 100), 1)
        df['employerPFContribution'] = np.round(
            np.where(df['employeeDepositAmount'] > 3600, df['employeeDepositAmount'] - 1250,
                     df['employeeDepositAmount'] * 36 / 100), 1)
        total = len(df)
        wScore = len(df[df['employerPFContribution'] > df['employerPensionContribution']])
        score = (wScore / total) * 1000

        records = df.T.to_dict().values()
        narrations = list(df['narration'])
        top_sources = topSources(narrations=narrations)
        next_25_years_estimation = get_pf_estimation(df)

    return construct_epf(
        str(data['type']).upper(),
        profile=profile,
        summary=summary,
        records=list(records),
        top_sources=top_sources,
        next_25_years_estimation=next_25_years_estimation,
        score=score
    )


def construct_epf(fi_type, profile, summary, records, top_sources, next_25_years_estimation, score):
    return {
        "type": fi_type,
        "profile": profile,
        "summary": summary,
        "records": records,
        "insights": {
            "topSources": top_sources,
            "next_25_years_estimation": "In next 25 years you will earn " + next_25_years_estimation + " Rupees"
        },
        "wealthScore": int(score if score > 100 else 100)
    }


def get_pf_estimation(df):
    ef = round(df['employerDepositAmount'].mean(), 2)
    year_salary = round((2 * ef * 12), 0)
    years = [year_salary] * 25 * 12
    years[0] = ef * 8.5
    return "{:,}".format(round(list(np.cumsum(years))[25 * 12 - 1], 2))


def CREDIT_CARD(data):
    records = None
    top_sources = None
    cd_max_min_ratio = None
    credit_vs_debit = None
    profile = None
    summary = None
    credit_score = 500
    if data['profile'] is not None:
        profile = data['profile']['holders']['holder']
    if data['summary'] is not None:
        summary = data['summary']
        if int(float(summary['totalDueAmount'])) < int(float(summary['creditLimit'])):
            credit_score += 100
        if int(float(summary['financeCharges'])) < 1000:
            credit_score += 100
        if int(float(summary['loyaltyPoints'])) > 1000:
            credit_score += 100

    if data['transactions'] is not None:
        df = getTransactions(data['transactions']['transaction'])
        df['txnDate'] = pd.to_datetime(df['txnDate'])
        df['txnDate'] = df['txnDate'].dt.tz_localize(None)
        df['amount'] = pd.to_numeric(df['amount'])
        df['amount'] = pd.to_numeric(df['amount'])
        df = df[['txnId', 'txnType', 'amount', 'narration', 'statementDate', 'txnDate']]
        df['narration'] = df['narration'].map(extractSpecialWords)
        records = df.T.to_dict().values()
        narrations = list(df['narration'])
        top_sources = topSources(narrations=narrations)
        c_d = df.groupby(["txnType"]).size().reset_index()
        c_d["percentage"] = (c_d[0] / c_d[0].sum()) * 100
        c_d["percentage"] = c_d["percentage"].round(decimals=2)
        c_d.drop(columns=[0], axis=1, inplace=True)
        credit_vs_debit = dict(zip(c_d['txnType'], c_d['percentage']))
        max_idx = df.groupby(['txnType'])['amount'].transform(max) == df['amount']
        max_infer = df[max_idx].sort_values('txnDate').groupby('txnType').tail(1)
        max_infer['txn_date'] = max_infer['txnDate'].dt.date
        min_idx = df.groupby(['txnType'])['amount'].transform(min) == df['amount']
        df[min_idx].sort_values('txnDate').groupby('txnType').tail(1)
        min_infer = df[min_idx].sort_values('txnDate').groupby('txnType').tail(1)
        min_infer['txn_date'] = min_infer['txnDate'].dt.date
        cd_max_min_ratio = {
            "max": {
                "credit": dict(max_infer.loc[max_infer['txnType'] == "CREDIT"].iloc[0]),
                "debit": dict(max_infer.loc[max_infer['txnType'] == "DEBIT"].iloc[0])
            },
            "min": {
                "credit": dict(min_infer.loc[min_infer['txnType'] == "CREDIT"].iloc[0]),
                "debit": dict(min_infer.loc[min_infer['txnType'] == "DEBIT"].iloc[0])
            }
        }

    return construct_credit(
        str(data['type']).upper(),
        profile=profile,
        summary=summary,
        records=list(records),
        top_sources=top_sources,
        cd=credit_vs_debit,
        ratio=cd_max_min_ratio,
        score=credit_score
    )


def construct_credit(fi_type, profile, summary, records, top_sources, cd, ratio, score):
    return {
        "type": fi_type,
        "profile": profile,
        "summary": summary,
        "records": records,
        "insights": {
            "topSources": top_sources,
            "creditVsDebit": cd,
            "creditMinMaxRatio": ratio,
        },
        "wealthScore": int(score if score > 100 else 100)
    }


def INSURANCE_POLICIES(data):
    records = None
    profile = None
    summary = None
    score = 100
    if data['profile'] is not None:
        profile = data['profile']['holders']
    if data['summary'] is not None:
        summary = data['summary']
        sumAssured = int(float(summary['sumAssured']))
        if sumAssured < 1000000:
            score = 500
        elif 1000000 < sumAssured < 2500000:
            score = 700
        else:
            score = 800

    if data['transactions'] is not None:
        df = getTransactions(data['transactions']['transaction'])
        df['txnDate'] = pd.to_datetime(df['txnDate'])
        df['txnDate'] = df['txnDate'].dt.tz_localize(None)
        df['amount'] = pd.to_numeric(df['amount'])
        df['narration'] = df['narration'].map(extractSpecialWords)
        records = df.T.to_dict().values()

    return construct_ip(str(data['type']).upper(), profile,
                        summary, records, score)


def construct_ip(fi_type, profile, summary, records, score):
    return {
        "type": fi_type,
        "profile": profile,
        "summary": summary,
        "records": list(records),
        "wealthScore": int(score if score > 100 else 100)
    }


def TERM_DEPOSIT(data):
    # Check for transactions Object present or not
    records = None
    top_sources = None
    credit_vs_debit = None
    cd_max_min_ratio = None
    top3_hourRange = None
    profile = None
    summary = None
    score = 100
    if data['profile'] is not None:
        profile = data['profile']['holders']
    if data['summary'] is not None:
        summary = data['summary']
    if data['transactions'] is not None:
        df = getTransactions(data['transactions']['transaction'])
        df['transactionTimestamp'] = pd.to_datetime(df['transactionTimestamp'])
        df['transactionTimestamp'] = df['transactionTimestamp'].dt.tz_localize(None)
        df['currentBalance'] = pd.to_numeric(df['currentBalance'])
        df['amount'] = pd.to_numeric(df['amount'])
        df = df[['mode', 'type', 'amount', 'narration', 'currentBalance', 'transactionTimestamp']]
        df['narration'] = df['narration'].map(extractSpecialWords)
        records = df.T.to_dict().values()
        # Top Sources
        narrations = list(df['narration'])
        top_sources = topSources(narrations=narrations)
        c_d = df.groupby(["type"]).size().reset_index()
        c_d["percentage"] = (c_d[0] / c_d[0].sum()) * 100
        c_d["percentage"] = c_d["percentage"].round(decimals=2)
        c_d.drop(columns=[0], axis=1, inplace=True)
        credit_vs_debit = dict(zip(c_d['type'], c_d['percentage']))
        max_idx = df.groupby(['type'])['amount'].transform(max) == df['amount']
        max_infer = df[max_idx].sort_values('transactionTimestamp').groupby('type').tail(1)
        max_infer['txn_date'] = max_infer['transactionTimestamp'].dt.date
        min_idx = df.groupby(['type'])['amount'].transform(min) == df['amount']
        df[min_idx].sort_values('transactionTimestamp').groupby('type').tail(1)
        min_infer = df[min_idx].sort_values('transactionTimestamp').groupby('type').tail(1)
        min_infer['txn_date'] = min_infer['transactionTimestamp'].dt.date
        cd_max_min_ratio = {
            "max": {
                "credit": dict(max_infer.loc[max_infer['type'] == "CREDIT"].iloc[0]),
                "debit": dict(max_infer.loc[max_infer['type'] == "DEBIT"].iloc[0])
            },
            "min": {
                "credit": dict(min_infer.loc[min_infer['type'] == "CREDIT"].iloc[0]),
                "debit": dict(min_infer.loc[min_infer['type'] == "DEBIT"].iloc[0])
            }
        }
        df['hour'] = df['transactionTimestamp'].dt.hour
        period = df.groupby(['type', 'hour']).size().reset_index(name='count')
        period = period.sort_values('count', ascending=False).groupby('type').head(3)
        top3_hourRange = {
            "credit": dict(
                zip(period.loc[period['type'] == "CREDIT"]['hour'], period.loc[period['type'] == "CREDIT"]['count'])),
            "debit": dict(
                zip(period.loc[period['type'] == "DEBIT"]['hour'], period.loc[period['type'] == "DEBIT"]['count']))
        }
        score = (100 - abs(credit_vs_debit["CREDIT"] - credit_vs_debit["DEBIT"])) * 10
    return construct_tdeposits(
        str(data['type']).upper(),
        profile=profile,
        summary=summary,
        records=list(records),
        top_sources=top_sources,
        cd=credit_vs_debit,
        ratio=cd_max_min_ratio,
        hour_range=top3_hourRange,
        score=round(score, 2)
    )


def construct_tdeposits(fi_type, profile, summary, records, top_sources, cd, ratio, hour_range, score):
    return {
        "type": fi_type,
        "profile": profile,
        "summary": summary,
        "records": records,
        "insights": {
            "topSources": top_sources,
            "creditVsDebit": cd,
            "creditMinMaxRatio": ratio,
            "peekHourCount": hour_range
        },
        "wealthScore": int(score if score > 100 else 100)
    }


def SIP(data):
    records = None
    sources_of_investment = None
    profile = None
    summary = None
    investedValue = 0
    currentValue = 0
    dataStory = ''
    profit = 10
    days = 0
    if data['profile'] is not None:
        profile = data['profile']['holders']
    if data['summary'] is not None:
        summary = data['summary']
        investedValue = int(float(summary['investmentValue']))
        currentValue = int(float(summary['currentValue']))
        profit = ((currentValue - investedValue) / investedValue) * 100

    if data['transactions'] is not None:
        df = getTransactions(data['transactions']['transaction'])
        str_time = getTime(data['transactions']['startDate'])
        end_time = getTime(data['transactions']['endDate'])
        df['txnDate'] = pd.to_datetime(df['txnDate'])
        df['txnDate'] = df['txnDate'].dt.tz_localize(None)
        if str_time is not None and end_time is not None:
            days = (end_time - str_time).days
        elif str_time is not None:
            days = date.today() - str_time
        else:
            days = "X"
        total = len(df)
        df["nav"] = getMockNav(50, total)
        df['units'] = pd.to_numeric(df['units'])
        df['amount'] = pd.to_numeric(df['amount'])
        records = df.T.to_dict().values()
        sources_of_investment = df['amc'].unique()

    if data['summary'] is not None and data['transactions'] is not None:
        dataStory = dataStory + "You have invested total of " + str(investedValue) + " in SIP "
        dataStory = dataStory + "After " + str(days) + " days it has become " + str(currentValue) + " and you are in"
        if profit > 0:
            dataStory = dataStory + " profit of " + str(round(profit, 2)) + "%"
        else:
            dataStory = dataStory + "Loss of " + str(round(profit, 2)) + "%"

    # return df
    return construct_SIP(str(data['type']).upper(), dataStory, profile, summary, sources_of_investment,
                         records, profit)


def getMockNav(value, n):
    pieces = []
    for idx in range(0, n):
        pieces.append(randint(value - 5, value + 5))
    return pieces


def construct_SIP(fi_type, data_story, profile, summary,
                  sources_of_investment, records, profit):
    return {
        "type": fi_type,
        "dataStory": data_story,
        "profile": profile,
        "summary": summary,
        "records": list(records),
        "insights": {
            "sourceOfInvestment": list(sources_of_investment),
            "profit/Loss": round(profit, 2)
        },
        "wealthScore": int(round(profit, 2) * 10 if round(profit, 2) * 10 > 100 else 100)
    }


def EQUITIES(data):
    records = None
    sources_of_investment = None
    profile = None
    summary = None
    investedValue = 0
    currentValue = 0
    dataStory = ''
    profit = 10
    days = 0
    if data['profile'] is not None:
        profile = data['profile']['holders']
    if data['summary'] is not None:
        summary = data['summary']
        investedValue = int(float(summary['investmentValue']))
        currentValue = int(float(summary['currentValue']))
        profit = ((currentValue - investedValue) / investedValue) * 100

    if data['transactions'] is not None:
        df = getTransactions(data['transactions']['transaction'])
        str_time = getTime(data['transactions']['startDate'])
        end_time = getTime(data['transactions']['endDate'])
        if str_time is not None and end_time is not None:
            days = (end_time - str_time).days
        elif str_time is not None:
            days = date.today() - str_time
        else:
            days = "X"
        df["strikePrice"] = pd.to_numeric(df['strikePrice'])
        df['units'] = pd.to_numeric(df['units'])
        df['tradeValue'] = pd.to_numeric(df['tradeValue'])
        df['totalCharge'] = pd.to_numeric(df['totalCharge'])
        records = df.T.to_dict().values()
        sources_of_investment = df['companyName'].unique()

    if data['summary'] is not None and data['transactions'] is not None:
        dataStory = dataStory + "You have invested total of " + str(investedValue) + " in SIP "
        dataStory = dataStory + "After " + str(days) + " days it has become " + str(currentValue) + " and you are in"
        if profit > 0:
            dataStory = dataStory + " profit of " + str(round(profit, 2)) + "%"
        else:
            dataStory = dataStory + "Loss of " + str(round(profit, 2)) + "%"

    # return df
    return construct_equities(str(data['type']).upper(), dataStory, profile, summary, sources_of_investment,
                              records, profit)


def construct_equities(fi_type, data_story, profile, summary,
                       sources_of_investment, records, profit):
    return {
        "type": fi_type,
        "dataStory": data_story,
        "profile": profile,
        "summary": summary,
        "records": list(records),
        "insights": {
            "sourceOfInvestment": list(sources_of_investment),
            "profit/Loss": round(profit, 2)
        },
        "wealthScore": int(round(profit, 2) * 10 if round(profit, 2) * 10 > 100 else 100)
    }
