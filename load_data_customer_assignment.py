import random
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import MiniBatchKMeans

seed = 10101
num_customers = 50000
num_candidates = 20
max_facilities = 8
num_clusters = 50
num_gaussians = 10
threshold = 0.99


def load_data():
  random.seed(seed)
  customers_per_gaussian = np.random.multinomial(num_customers,
                                                [1/num_gaussians]*num_gaussians)
  customer_locs = []
  for i in range(num_gaussians):
      # each center coordinate in [-0.5, 0.5]
      center = (random.random()-0.5, random.random()-0.5)
      customer_locs += [(random.gauss(0,.1) + center[0], random.gauss(0,.1) + center[1])
                    for i in range(customers_per_gaussian[i])]
  # each candidate coordinate in [-0.5, 0.5]
  facility_locs = [(random.random()-0.5, random.random()-0.5)
                for i in range(num_candidates)]
  print('First customer location:', customer_locs[0])

  kmeans = MiniBatchKMeans(n_clusters=num_clusters, init_size=3*num_clusters,
                          random_state=seed).fit(customer_locs)
  memberships = list(kmeans.labels_)
  centroids = list(kmeans.cluster_centers_) # Center point for each cluster
  weights = list(np.histogram(memberships, bins=num_clusters)[0]) # Number of customers in each cluster
  print('First cluster center:', centroids[0])
  print('Weights for first 10 clusters:', weights[:10])

  def dist(loc1, loc2):
      return np.linalg.norm(loc1-loc2, ord=2) # Euclidean distance

  pairings = {(facility, cluster): dist(facility_locs[facility], centroids[cluster])
              for facility in range(num_candidates)
              for cluster in range(num_clusters) 
              if  dist(facility_locs[facility], centroids[cluster]) < threshold}
  print("Number of viable pairings: {0}".format(len(pairings.keys())))
  return customer_locs, centroids, facility_locs, pairings, weights
