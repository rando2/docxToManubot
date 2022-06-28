# updateStats and finalizeStats are an implementation of Welford's online algorithm taken from Wikipedia:
# https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Online_algorithm

def initStats(scores):
    count = len(scores)
    mean = sum(scores) / count
    squaredDist = 0
    for score in scores:
        squaredDist += (score - mean)**2
    return (count, mean, squaredDist)

def updateStats(existingAggregate, newValue):
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
    (count, mean, M2) = stats
    sampleVariance = M2 / (count - 1)
    return (currentVal - mean) / sampleVariance
