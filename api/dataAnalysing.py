def topSources(narrations):
    top_sources = {
        "Bank": 0,
        "Insurance": 0,
        "Others": 0
    }
    for firstValue in narrations:
        uFirstValue = firstValue.upper()
        if "BANK" in uFirstValue or "CARD" in uFirstValue or "Loan" in uFirstValue:
            top_sources["Bank"] = top_sources["Bank"] + 1
        elif "INS" in uFirstValue:
            top_sources["Insurance"] = top_sources["Insurance"] + 1
        else:
            top_sources['Others'] = top_sources['Others'] + 1
    return top_sources
