from sklearn.tree import DecisionTreeClassifier, plot_tree
import matplotlib.pyplot as plt
import pandas as pd

data = {
    'Genre_Action': [1, 0, 0, 1, 0, 0, 1, 1, 0, 0],
    'Genre_Comedy': [0, 1, 1, 0, 1, 1, 0, 0, 1, 1],
    'Average_Rating': [4.7, 3.5, 4.0, 4.8, 3.6, 4.2, 4.5, 4.1, 3.9, 3.2],
    'Year': [2020, 2015, 2018, 2021, 2010, 2017, 2022, 2019, 2016, 2014],
    'Recommend': [1, 0, 1, 1, 0, 1, 1, 1, 0, 0],
}

df = pd.DataFrame(data)
X = df[['Genre_Action', 'Genre_Comedy', 'Average_Rating', 'Year']]
y = df['Recommend']

model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X, y)

# Plot the decision tree
plt.figure(figsize=(12, 8))
plot_tree(
    model,
    feature_names=['Genre_Action', 'Genre_Comedy', 'Average_Rating', 'Year'],
    class_names=['Do Not Recommend', 'Recommend'],
    filled=True,
    rounded=True
)
plt.title("Decision Tree for Movie Recommendation System")
plt.show()