# Titanic Analytics and Modeling

## Project Overview

This module analyzes the classic Titanic dataset using exploratory data analysis, statistical analysis, machine learning classification, class-imbalance techniques, hyperparameter tuning, and regression.

The dataset was loaded once using Seaborn and immediately saved as `titanic.csv`. The same dataset was then cleaned and used for both EDA and modeling.

## Files

* `01_eda.ipynb` — Complete Titanic EDA, classification, imbalance analysis, hyperparameter tuning, and regression workflow.
* `titanic.csv` — Raw Titanic dataset saved immediately after loading.
* `best_model_pipeline.joblib` — Saved Random Forest pipeline containing preprocessing and the fitted estimator.

## 1. Data Loading and Profiling

The Titanic dataset was loaded using:

```python
sns.load_dataset("titanic")
```

The raw dataset contained:

* 891 rows
* 15 columns

The raw dataset was immediately saved as `titanic.csv` before any cleaning.

### Missing Values

| Column        | Missing Percentage | Treatment         |
| ------------- | -----------------: | ----------------- |
| `age`         |             19.87% | Median imputation |
| `embarked`    |              0.22% | Rows dropped      |
| `deck`        |             77.22% | Column dropped    |
| `embark_town` |              0.22% | Rows dropped      |

The missing-value policy followed the assignment thresholds:

* Less than 5%: drop affected rows.
* 5–30%: impute.
* More than 30%: drop the column with justification.

`deck` was removed because 77.22% of its values were missing. The two rows missing `embarked` and `embark_town` were removed. Missing `age` values were replaced using the median age.

After cleaning, the working dataset contained 889 rows and 14 columns.

## 2. Exploratory Data Analysis

### Age and Fare

Histograms and box plots were created for `age` and `fare`.

IQR outlier analysis found:

* Age: 65 potential outliers
* Fare: 114 potential outliers

The outliers were identified but not removed because they represent genuine variation in passenger age and fare.

### Fare Summary

* Mean: 32.0967
* Median: 14.4542
* Mode: 8.05

Because the mean is substantially higher than the median and mode, the fare distribution is right-skewed.

## 3. Survival Analysis

### Survival Rate by Sex

* Male: 18.89%
* Female: 74.04%

### Survival Rate by Passenger Class

* First class: 62.62%
* Second class: 47.28%
* Third class: 24.24%

### Survival Rate by Sex and Passenger Class

| Group           | Survival Rate |
| --------------- | ------------: |
| Male, Class 1   |        36.89% |
| Male, Class 2   |        15.74% |
| Male, Class 3   |        13.54% |
| Female, Class 1 |        96.74% |
| Female, Class 2 |        92.11% |
| Female, Class 3 |        50.00% |

Boolean masking with `&` and `|` was used for subgroup analysis.

## 4. Correlation Analysis

The correlation matrix used exactly these six columns:

* `survived`
* `pclass`
* `age`
* `sibsp`
* `parch`
* `fare`

The two strongest absolute correlations were:

1. `pclass` and `fare`: -0.5482
2. `sibsp` and `parch`: 0.4145

The negative correlation between passenger class and fare reflects the coding of `pclass`, where a higher class number represents a lower passenger class and generally lower fares.

The positive correlation between `sibsp` and `parch` indicates that passengers traveling with more siblings/spouses also tended to travel with more parents/children.

## 5. Multivariate Visualizations

Four multivariate charts were created:

1. Survival rate by sex and passenger class.
2. Age versus fare by survival status and sex.
3. Age distribution by passenger class and survival status.
4. Fare distribution by passenger class and survival status.

These visualizations show that survival was associated with both sex and passenger class, while age and fare distributions showed substantial overlap between survivors and non-survivors.

## 6. EDA-Only Standardization

Z-score standardization was applied to `age` and `fare` for EDA purposes only.

Before standardization:

* Age mean: 29.3152
* Age standard deviation: 12.9776
* Fare mean: 32.0967
* Fare standard deviation: 49.6695

After standardization:

* Age mean: approximately 0
* Age standard deviation: 1
* Fare mean: approximately 0
* Fare standard deviation: 1

These standardized variables were not used as inputs to the modeling pipeline.

# Machine Learning

## 7. Train/Test Split

A stratified train/test split was used so that the proportion of survived and non-survived passengers remained approximately consistent between training and testing data.

The final test set contained 178 observations.

The training class distribution was:

* Not survived: 439 (61.74%)
* Survived: 272 (38.26%)

This represents moderate class imbalance, making stratification appropriate.

## 8. Modeling Features and Preprocessing

The classification models used:

* `pclass`
* `sex`
* `age`
* `sibsp`
* `parch`
* `fare`
* `embarked`

Features such as `alive`, `class`, `who`, `adult_male`, `alone`, and `embark_town` were excluded because they were direct outcome information, duplicates, or derived/redundant variables.

Preprocessing was implemented using `ColumnTransformer` and `Pipeline`.

### Numeric Features

* Median imputation
* StandardScaler

### Categorical Features

* Most-frequent imputation
* One-hot encoding
* `handle_unknown="ignore"`

All preprocessing was fitted within the training pipeline to avoid data leakage.

## 9. Classification Models

Three classification models were trained on the same stratified split:

* Logistic Regression
* Decision Tree
* Random Forest

A Decision Tree visualization was also created using `plot_tree`, including feature names and class labels.

### Classification Results

| Model               | Accuracy | Precision | Recall |     F1 | ROC-AUC |
| ------------------- | -------: | --------: | -----: | -----: | ------: |
| Logistic Regression |   0.8090 |    0.7833 | 0.6912 | 0.7344 |  0.8610 |
| Decision Tree       |   0.7640 |    0.7600 | 0.5588 | 0.6441 |  0.8374 |
| Random Forest       |   0.8090 |    0.7656 | 0.7206 | 0.7424 |  0.8196 |

Confusion matrices were generated for all three models.

## 10. Class Imbalance

The baseline Logistic Regression model was compared with:

* Class-weighted Logistic Regression
* SMOTE Logistic Regression

| Approach       | Precision | Recall |     F1 |
| -------------- | --------: | -----: | -----: |
| Baseline       |    0.7833 | 0.6912 | 0.7344 |
| Class Weighted |    0.7183 | 0.7500 | 0.7338 |
| SMOTE          |    0.7353 | 0.7353 | 0.7353 |

Class weighting increased recall from 0.6912 to 0.7500 while reducing precision.

SMOTE produced equal precision and recall of 0.7353 and resulted in an F1-score of 0.7353.

SMOTE was applied only within the training pipeline.

## 11. Random Forest Hyperparameter Tuning

GridSearchCV was used with 5-fold cross-validation.

Parameters searched:

* `n_estimators`: 100, 200, 300
* `max_depth`: None, 5, 10
* `max_features`: `sqrt`, `log2`

The search used F1-score as the optimization metric.

Best parameters:

```text
max_depth = None
max_features = sqrt
n_estimators = 300
```

Best cross-validation F1-score:

```text
0.7449
```

The tuned Random Forest OOB score was:

```text
0.8073
```

Tuned Random Forest test metrics:

* Accuracy: 0.8034
* Precision: 0.7619
* Recall: 0.7059
* F1: 0.7328
* ROC-AUC: 0.8237

## 12. Fare Regression

A multivariate Linear Regression model was used to predict `fare` from other available Titanic features.

Predictors included:

* `survived`
* `pclass`
* `sex`
* `age`
* `sibsp`
* `parch`
* `embarked`

Results:

| Metric      |   Value |
| ----------- | ------: |
| MAE         | 21.0986 |
| RMSE        | 41.7021 |
| R²          |  0.3482 |
| Adjusted R² |  0.3091 |

A residual plot was created to assess model assumptions.

The residual spread widens as predicted fare increases, indicating heteroscedasticity. Therefore, the constant-variance assumption of ordinary linear regression is not fully satisfied.

## 13. Final Model Selection

For the Titanic classification task, the Random Forest achieved the highest test-set F1-score among the three original classifiers at 0.7424, with an accuracy of 0.8090 and recall of 0.7206. Logistic Regression achieved the highest ROC-AUC at 0.8610 and the highest precision at 0.7833, while the Decision Tree had an F1-score of 0.6441. The tuned Random Forest achieved a cross-validation F1-score of 0.7449 and an OOB score of 0.8073, but its test-set F1-score was 0.7328.

The final saved classification pipeline uses the original Random Forest because it achieved the highest test-set F1-score among the original classifiers and stronger recall than Logistic Regression. The imbalance experiments showed that class weighting increased recall to 0.7500, while SMOTE produced balanced precision and recall of 0.7353. For fare prediction, Linear Regression achieved an MAE of 21.0986, RMSE of 41.7021, R² of 0.3482, and adjusted R² of 0.3091, with the residual plot indicating heteroscedasticity.

## 14. Saved Model Pipeline

The selected Random Forest model was saved together with its complete preprocessing pipeline:

```text
best_model_pipeline.joblib
```

The saved pipeline was reloaded using `joblib.load()` and successfully generated a prediction from raw input data.

For the test passenger used during validation:

* Predicted survival: `0`
* Actual survival: `0`

This confirms that preprocessing and prediction can be performed through the single saved pipeline without manually transforming the raw input.
