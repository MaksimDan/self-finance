# Todo

## testing

* need to figure out a way to mock the front end endpoints flask routes mock (should be well known problem just have to research it)
* Prob want to later even expose the tests from the gitignore, will need to anon first

## installation

* add windows installable
* do you need a MANIFEST.in file? https://python-packaging.readthedocs.io/en/latest/non-code-files.html

## bugs

* index not flashing
  * in general flashing has been behaving pretty strange in the sense that it would flash on the next page.
* when drawing - catch exceptions, since some plots kight fail - and report the ones that failed back to the user.
* problamatic plots:
    * might want to start up with plotly.
    * income by month/expenses by month- bar
        * xaxis text not readable
        * too crowded with full range
        * and it doesnt actually seperated by month (strictly). so it doesnt work. (it should operate by months within this range.)
            * fix == grab the month intoa  new col and then group by there uniquely not reploy on pandas time group by internal


## big - high priority

* add ployly suport instead. WAYYYYYYYYYYYYYY better
* convert the configs to raw constant values without a class, so they can be intelligently parsed 
* insights
  * TODO: look at what sorts of things other poeple included in their analysis from spread sheet documents for example. Jot out the ideas here:
    * queryable insights
    * static insights
      * predictions: dependency model predictions
        * your expected income in 1 month, 6 months, 1 year, 5 years, and 10 years
        * your expected expenses ... etc


## medium - mid priority

* Projections: would need to tabularize /visuals tab to include everything
  * refactoring previous ml code
  * updating the model per every filter.

## small - low priority

* Hide transaction id from bank table, and rename schema
* depricate the models
* disallow get methods when they should be posts.

## optional enhancements

* more flask status messages
* add log statements everywhere it is important
* add objs: and optimize imports / refactor code, doc strings
* in `Select Plots to Visualize`make this not grown down, have breakpoints and then display inline rather than being row based , google it
* html could use some more clean up or robustness -- <http://jinja.pocoo.org/docs/2.10/intro/> has some good stuff
    * you have form names in the html even when they are not nessessary
    * making the naming conventions in the html consistent, for example all the ids following some pattern, or the names ... etc. e.g. `visuals_redraw_form`for forms 
* prograss bar for the visualizers, would be useful in other contexts too like POST /index/update_transactions...
    * https://stackoverflow.com/questions/24251898/flask-app-update-progress-bar-while-function-runs/40810805
    * try to write your own progressbar, that can be generically used for your use case.
- preprocessing step: use google api to get the lat and lon from the city itself, unless provided. using location column, if anything else is available like city.
* exposing all the constants in settings, files.py. need option to write and reset. not required, but good for transparancy.

