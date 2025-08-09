import math

from sklearn.metrics import confusion_matrix, roc_curve, auc, classification_report
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import shap


def display_confusion(real, predicted, decision_threshold=0.5):
    y_pred = [1 if p > decision_threshold else 0 for p in predicted]

    linear_confusion = confusion_matrix(real, y_pred)
    plt.figure(figsize=(4, 3))
    sns.heatmap(linear_confusion, annot=True, fmt="", cmap='Blues', cbar=False,
                xticklabels=['Predicted 0', 'Predicted 1'], yticklabels=['Actual 0', 'Actual 1'])


def display_classification_report(real, predicted, decision_threshold=0.5):
    y_pred = [1 if p > decision_threshold else 0 for p in predicted]
    print(classification_report(real, y_pred))


def display_roc(real, predicted, decision_threshold=0.5):
    y_pred = [1 if p > decision_threshold else 0 for p in predicted]
    fpr, tpr, thresholds = roc_curve(real, y_pred)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(7, 4))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')  # Diagonal line
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend(loc='lower right')
    plt.show()


def display_correlation(predictors):
    correlation_matrix = predictors.corr()

    sns.set(style="white")

    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(correlation_matrix, mask=mask, cmap=cmap, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5})

    # Show the heatmap
    plt.show()


def display_shap_tree_summary(tree, predictors):
    # Create the SHAP explainer object
    explainer = shap.TreeExplainer(tree)

    # Calculate SHAP values for the training set
    shap_values = explainer.shap_values(predictors)

    # Summary plot of SHAP values for all features
    shap.summary_plot(shap_values, predictors)


def display_predictor_pdf(subset, subset_name):
    preds = [('weightLbsTotal', 'Weight (lbs)'),
             ('largestDimIn', 'Largest Dimension (in)'),
             ('distanceMi', 'Distance (mi)')]
    display_predictor_pdfs(subset, subset_name, preds)

def display_predictor_pdfs(subset, subset_name, predictors: list[tuple[str, str]]):
    n_rows = math.ceil(len(predictors) / 3)
    fig, axes = plt.subplots(n_rows, 3, figsize=(12, 3 * n_rows))
    axes = axes.flatten()  # Flatten to make indexing simpler

    for i, (predictor_col, predictor_name) in enumerate(predictors):
        values = np.sort(subset[predictor_col])

        axes[i].hist(values, bins=50, density=True, alpha=0.6,
                     label=f'{predictor_name} Density')  # density=True ensures area sums to 1
        axes[i].set_xlabel(f'{predictor_name}')
        axes[i].set_ylabel('Probability Density')
        axes[i].set_title(f'{subset_name} {predictor_name} (PDF) Plot')
        axes[i].legend()
        axes[i].grid(True)

    # Hide any unused subplots
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')

    plt.tight_layout()
    plt.show()