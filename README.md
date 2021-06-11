# SAS-Project-Unbalanced-Classes




<br />
<p align="center">
  <a href="#">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/SAS_logo_horiz.svg/1280px-SAS_logo_horiz.svg.png" alt="Logo" height="80">
  </a>

  <h3 align="center">SAS Project</h3>
  <h3 align="center">Unbalanced Classes</h3>
  <h3 align="center">HSE 2021</h3>
  

  <p align="center">
    Prepared by <br />
   <b align="center"> Zobov Vladimir, 
    Karzanov Daniil, 
    Molostvov Pavel </b>
  
  <br />
  Supervisor: <b>Maria Vorobyova </b><br />

  </p>
</p>



main.ipynb notebook contain the python implementation of the following items:
* Data analysis
For us, the most important thing is to minimize the number of real defaults that were classified as non-default, that is, after the selection of clients by the model, the bank would receive as few clients who would not be able to repay the loan, as possible. However, it is also important that the number of issued loans does not decrease significantly after the model has been run. That is why we will use two metrics to asses model's performance: FOR (False Ommition Rate) will show how many clients, of which the model offered to issue a loan, will be defaulters and FPR (False Positive Rate) will show how many of all non-defaulters were denied a loan by the model. By minimizing both metrics we will achieve the best model. 

* Feature engineering


There are a few methods to deal with imbalanced target. We will try some under and over-sampling techniques as well as special models that rebalance target while fitting. Also we will try simply to increase treshold, oftentimes it is sufficient to have really good results. 
* Undersampling 

Undersampling is a group of techniques that consists of reducing the data by eliminating examples belonging to the majority class with the objective of equalizing the number of examples of each class.

* * Random undersampling
* * Tomek link
* * InstanceHardnessThreshold
* * NeighbourhoodCleaningRule
* Oversampling
* * Random oversampling 
* * Smote
* * Adasyn
* Models that rebalance target while fitting
* * EasyEnsembleClassifier
* * RUSBoostClassifier
* * BalancedBaggingClassifier
* * BalancedRandomForestClassifier
* Model evaluation and model selection
* Profitability of model evaluation
* Conclusion

Also, the telegram bot was implemented in Scoring_bot/Scoring.py contains the best model. The bot allows a user to fill the form and learn if he or she may receive a loan.
![image](https://user-images.githubusercontent.com/49778314/121660273-cd72c000-caab-11eb-9a7e-c67b10779ab5.png)

We can see that there are 5 models that perform better than others: No resampling, Easy Ensemble, Balanced Random Forest, Random Underdampling, Random Oversampling. Now we will test them in terms of best profit that they can give us. We will assume that average debt on credit card is the same for clients who default and not default. Also we will assume that that in case of default we lose all the money that client paid from his credit card and we will use interest rate of 20, because it is most near value to the real credit card interests in US dollars now.

We can see that with Stacking of Balanced Random Forest, Catboost and XGBoost we can get the best result by profit. Surprisingly, this model has been trained on resampled data (Stacking with Balanced Random Forest but trained on original data is not shown, but its result was worse), so we could conclude that additional balanced fitting after undersampling also has a positive influence to the model. This model gives us 15% increase in revenue, which is significant improvment for the bank. Also I would like to draw your attention on CatBoost model. Its financial result is as good as in the best model, but number of clients in this model greater than in others. Bank may use  this model if they are also interested in attracting clients to different products throught credit cards.

