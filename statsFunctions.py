# updateStats and finalizeStats are an implementation of Welford's online algorithm taken from Wikipedia:
# https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Online_algorithm
import numpy as np

def initStats(scores):
    count = sum(~np.isnan(scores))
    mean = np.nansum(scores) / count
    squaredDist = 0
    for score in scores:
        if not np.isnan(score):
            squaredDist += (score - mean)**2
    return (count, mean, squaredDist)

def updateStats(existingAggregate, newValue):
    if np.isnan(newValue):
        return existingAggregate

    (count, mean, M2) = existingAggregate
    count += 1
    delta = newValue - mean
    mean += delta / count
    delta2 = newValue - mean
    M2 += delta * delta2
    return (count, mean, M2)

# Retrieve the mean, variance and sample variance from an aggregate
def finalizeStats(existingAggregate):
    (count, mean, M2) = existingAggregate
    if count < 2:
        return float("nan")
    else:
        (mean, variance, sampleVariance) = (mean, M2 / count, M2 / (count - 1))
        return (mean, variance, sampleVariance)

def retrieveZ(stats, currentVal):
    if np.isnan(currentVal):
        return float("nan")

    (count, mean, M2) = stats
    sampleVariance = M2 / (count - 1)
    return (currentVal - mean) / sampleVariance
