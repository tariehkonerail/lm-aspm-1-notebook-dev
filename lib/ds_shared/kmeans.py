from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt


def elbow_fit(features, candidate_range):
    # Determine the number of clusters for a range of k
    wcss = []
    k_candidates = candidate_range

    for k in k_candidates:
        print(f"Fitting KMeans for k={k}")  # Optional: to track progress
        kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
        kmeans.fit(features)
        wcss.append(kmeans.inertia_)

    # Plot the elbow curve
    plt.figure(figsize=(10, 8))
    plt.plot(k_candidates, wcss, 'bo-', markerfacecolor='red')
    plt.title('Elbow Method For Optimal k')
    plt.xlabel('Number of clusters')
    plt.ylabel('WCSS (Inertia)')
    plt.xticks(k_candidates, rotation=90)  # Rotate x-axis labels for better readability
    plt.grid(True)
    plt.show()


def silhouette_fit(features, candidate_range):
    silhouette_scores = []
    k_candidates = candidate_range

    for k in k_candidates:
        print(f"Fitting KMeans for k={k}")  # Optional: to track progress
        kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
        kmeans.fit(features)
        score = silhouette_score(features, kmeans.labels_)
        silhouette_scores.append(score)

    # Plot the silhouette scores
    plt.figure(figsize=(10, 8))
    plt.plot(k_candidates, silhouette_scores, 'bo-', markerfacecolor='red')
    plt.title('Silhouette Score for Various Numbers of Clusters')
    plt.xlabel('Number of clusters')
    plt.ylabel('Silhouette Score')
    plt.xticks(k_candidates, rotation=90)  # Rotate x-axis labels for better readability
    plt.grid(True)
    plt.show()
