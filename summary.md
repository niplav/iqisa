GJOpen Data: Description
=========================

The data in the dataset was collected over four years of forecasting.

In every year, the Good Judgement Project (from here on GJP)
collected forecasts by surveying forecasters (aggregated in the files
`survey_fcasts.yr{1,2,3,4}.csv`). Additionally, from year 2 onwards,
they also ran prediction markets to determine probabilities.

### Prediction Markets

2. For the second year, the prediction market was a continuous [double auction](https://en.wikipedia.org/wiki/Double_auction) (CDA) market run by the company [Lumenogic](https://www.hypermind.com/en/lumenogic-becomes-hypermind/), in which the forecasters participated without forming teams.
3. In year three, there were four different prediction markets.
	* Three CDA markets, run by Lumenogic:
		* `lum1`, in which only US participants could participate, without teams
		* `lum2a`, in which everyone could participate, without teams
		* `lum2`, in which everyone could participate, which switched from individuals to teams halfway through year three (2014)
	* One logarithmically scored prediction market (LMSR) run by Inkling ([their website](https://www.inklingmarkets.com/) seems down?), without teams
4. For the fourth year, there were five prediction markets, all run by Inkling.
	* First market: similar to the Inkling market in year three<!--TODO: what is an IFP in the context of markets?-->
	* The other four markets used an "IFP" (not sure what that means, could either be an [Intelligent Forecasting Platform](https://www.pwc.com/gr/en/advisory/data-and-analytics/intelligent-forecasting-platform.html) or a [factor](https://financial-dictionary.thefreedictionary.com/IFP)?)
		* `supers`, for the previous years superforecasters
		* `batch.train`, for any participants from the previous year
		* `teams`, for participants in teams
		* `batch.notrain`, with no specificities

### Identifying Forecasters & Teams

Forecasters are identified by the fields

* `user_id` everywhere, except:
* `userid_yr4` for year 4 (those can be mapped to each other with information from the `all_individual_differences.csv` file),
* `user.ID` for the year 2 prediction market data,
* `gjp.user.id` for year 3 Inkling prediction market data,
* `User.ID` for year 3 Lumenogic prediction market data, and
* `GJP.User.ID` for year 4 prediction market data

Teams are identified by the fields

* `team` everywhere, except
* `Team` in the year 3 Lumenogic prediction market data, and
* `GJP.Team.ID` in the year 4 prediction market data

It is not clear how to map individual forecasters to teams: Was there
a one-to-one mapping from a forecaster and a year to a team? Or could
a forecaster be in multiple different teams during a single year? Or
were there only stable teams for all years? I don't know, and online
resources aren't very clear on this.<!--TODO: check a bit more deeply,
maybe look what the data says-->

It is possible to map users to teams via the
`survey_fcasts_yr{1,2,3,4}.csv` files. Looking at those files, in year
one there is no user who participated in more than 1 group (and plenty who
participated in no groups at all). In year two there is one user (ID 2067)
who made forecasts both from a group (group 4) *and* outside of a group.
In year three the user 1095 made forecasts both from groups 1 *and* 4,
and in year 4 there are again no such duplicate groups.

<!--TODO: message the GJP people about this?-->

Three cheers for data clarity!

Files
------

### `ifps.csv`

This file contains the data concerning questions and their outcomes,
one question per line.

#### Invalid Characters

Contains some stray invalid characters which
cause trouble while parsing the CSV with Python.

First, the data uses carriage return both in fields and to separate
fields. *sigh*.

We can solve this with the following command:

	sed 's/\r([0-9]+-[0-9]+)/\n\1/g' <ifps.csv >ifps_new.csv
	mv ifps_new.csv ifps.csv

Then the file also contains some *other* characters that shouldn't belong
there either.

	tr -d '[ -~]\n\t' <ifps.csv | od -A x -t x1 | sed 's/^[0-9a-f]+ ?//' | tr ' ' '\n' | sort | uniq -c
	      1 
	      1 aa
	      1 db
	      1 e5
	      2 89
	      4 a9
	      4 bb
	      4 ed
	     11 9d
	     11 ec
	     30 f3
	     31 e4
	     62 e6
	     68 8c

`file -k` classifies the file as "ifps.csv: CSV text\012- , Non-ISO
extended-ASCII text, with very long lines". The stray "bad" characters
can be removed via

	tr -dc '[ -~]\n\t' <ifps.csv >ifps_new.csv
	mv ifps_new.csv ifps.csv

An example part of the `diff` then looks like this:

	-1113-6,6,When will Viktor Orban resign or otherwise vacate the office of Prime Minister of Hungary?,"Outcome will be resolved ""Event will not occur before 1 April 2013"" if Orban holds the position of Prime Minister at this time and has not resigned or suffered confidence vote defeat. Death of Orban constitutes vacation of office; temporary incapacitation due to routine medical procedure does not. <8C><E6>Whether prolonged medical incapacitation (e.g. coma) constitutes vacation of office will be determined on a case-by-case basis by a subject matter expert familiar with Hungarian succession law. <8C><E6>A formal announcement or letter of intent to resign that lists a specific date will be treated as constituting resignation. <8C><E6>Outcome will be resolved based on reporting from one or more of the following sources:<8C><E6>BBC<8C><E6>News or Reuters or Economist Online (http://www.bbc.co.uk/news/<8C><E6>or<8C><E6>http://www.reuters.com/<8C><E6>orhttp://www.economist.com). If nothing is reported in these sources, then the ""status quo"" outcome typically will be assumed (e.g., for a question about a political leader leaving office, an absence of reporting will be taken to indicate that the leader remains in office). <8C><E6>Administrator<8C><E6>reserves the right to use other sources as needed (e.g.,<8C><E6>CIA<8C><E6>World Factbook, Wikipedia), provided those sources do not directly contradict concurrent event reporting from<8C><E6>BBC<8C><E6>News, Reuters, or Economist Online. In cases of substantial controversy or uncertainty,<8C><E6>Administrator<8C><E6>may refer the question to outside subject matter experts, or we may deem the question invalid/void. Before should be interpreted to mean at or prior to the end (11:59:59 ET) of the previous day. ",closed,6/25/12,3/30/13 0:00,3/31/13,3/31/13,d,Orban vacate PM of Hungary,279,4,"(a) Between 1 Jul 2012 and 30 Sep 2012, (b) Between 1 Oct 2012 and 31 Dec 2012, (c) Between 1 Jan 2013 and 31 Mar 2013, (d) Event will not occur before 1 April 2013"
	+1113-6,6,When will Viktor Orban resign or otherwise vacate the office of Prime Minister of Hungary?,"Outcome will be resolved ""Event will not occur before 1 April 2013"" if Orban holds the position of Prime Minister at this time and has not resigned or suffered confidence vote defeat. Death of Orban constitutes vacation of office; temporary incapacitation due to routine medical procedure does not. Whether prolonged medical incapacitation (e.g. coma) constitutes vacation of office will be determined on a case-by-case basis by a subject matter expert familiar with Hungarian succession law. A formal announcement or letter of intent to resign that lists a specific date will be treated as constituting resignation. Outcome will be resolved based on reporting from one or more of the following sources:BBCNews or Reuters or Economist Online (http://www.bbc.co.uk/news/orhttp://www.reuters.com/orhttp://www.economist.com). If nothing is reported in these sources, then the ""status quo"" outcome typically will be assumed (e.g., for a question about a political leader leaving office, an absence of reporting will be taken to indicate that the leader remains in office). Administratorreserves the right to use other sources as needed (e.g.,CIAWorld Factbook, Wikipedia), provided those sources do not directly contradict concurrent event reporting fromBBCNews, Reuters, or Economist Online. In cases of substantial controversy or uncertainty,Administratormay refer the question to outside subject matter experts, or we may deem the question invalid/void. Before should be interpreted to mean at or prior to the end (11:59:59 ET) of the previous day. ",closed,6/25/12,3/30/13 0:00,3/31/13,3/31/13,d,Orban vacate PM of Hungary,279,4,"(a) Between 1 Jul 2012 and 30 Sep 2012, (b) Between 1 Oct 2012 and 31 Dec 2012, (c) Between 1 Jan 2013 and 31 Mar 2013, (d) Event will not occur before 1 April 2013"

#### Dates are not ISO-8601

Instead, they use the American date format (ugh). Use `strptime` or a
similar function to parse them.

#### Relevant Fields

* `ifp_id`: Refers to the question identifier
* `q_type`: Type of the question
	* Value of 0: Either a standard "bimodal" question (nomenclature by Tetlock's group, 2 outcomes, also commonly known as a binary question) or a "multimodal" question (with 3 or more outcomes)
	* Value of 1-5: Conditional questions?<!--TODO-->
	* Value of 6: An ordered "multimodal" question (example: When will X happen? 4 different date ranges given)
		* This is distinguished from `q_type` 0 because they score ordered questions differently

### `all_individual_differences.csv`

A barrage of results from psychometric tests on the individual
forecasters.

### `survey_fcasts.yr{1,2,3,4}.csv`

These files contain individual non-prediction market forecasts.

In the file `survey_fcasts.yr1.csv` there are a couple of forecasts made
by the unpersoned user "NULL". I don't know what this means: I suspected
at first that those were forecasts on "voided" questions, but it turns
out that that's not the case. The user "NULL" doesn't occur in any other
of those four files.

### `pm_*`

These files contain information for the prediction markets.

They also sometimes contain the true probabilities believed by the
traders:

* The field `Tru.Belief` in the files `pm_transactions.lum1.yr3.csv`, `pm_transactions.lum2.yr3.csv` and `pm_transactions.lum2a.yr3.csv`
* The field `probability_estimate` in the files `pm_transactions.inkling.yr3.csv`
