# insider-transactions
<img src="images/title_card.png" alt="Alt text" title="Leading Asset Movement" width="520" height="293">
"When it
		reaches fifty, you can let out a
		little taste to your friends.
		Then call this number -- 555-7617:
		tell the man "blue horseshoe loves
		Anacott Steel..." You scored, Buddy!
		Be in touch." - Gordon Gekko

# introduction
The insider transactions project affectionately named “Anacott” after the famous line “Blue horseshoe loves Anacott Steel” from the 1987 film Wall Street, is an attempt to analyze insider buying and selling of securities to determine if there was any alpha to be generated from directly following these insider transactions and how reliable this alpha is if any.

Fist things first, we need some insider transaction information. The website openinsider.com is a phenomenal resource for anyone looking to review or follow insider buying, selling, awards, and option exercises. I really can’t say enough great things about the site. We’ll be collecting all transactions regardless of company and industry that are:

1.	Buys
2.	An Officer (COB, CEO, Pres. COO, CFO, GC, VP)
3.	Dollar value > $300,000


The reasoning for these conditions are that an insider would only purchase stock in their company if they predict the stock will do well. No one is personally tying themselves to a sinking ship. They may sell stock for several reasons. Option exercises, prescription to a 10b-5 trading plan, the short or long term outlook for the company/market is not ideal, etc.. 

For these reasons we restrict the collection to Buys. Strictly officer purchases are since they are more aware of day-to-day operations and will be information generators whereas directors are receiving as reacting to the information. The $300,000 minimum transaction value also ensures that the buyer is somewhat financially committed to their investment, and they are more likely to have actionable information behind their decision. 

After defining this information collection threshold, we request ~5000 transactions that happened at least 1-month prior to todays date and save them as a .csv file for operation. If for whatever reason, you think to use .tsv file instead, I respect your opinion, but you’re wrong. 
I ended up doing some preliminary cleaning in excel for my own peace of mind. This mainly was converting the position of the buyer to an integer representing the highest station they were holding at the time of purchase. i.e. CEO -> 0, COB -> 1 …. Etc. . If they held more than one position like CEO & COB, the higher rated position is retained for analysis. 

After this initial cleaning, the data was ready for some real work.  Below pictured is the raw form data that we will begin working on. To evaluate and smooth returns from these stocks, I will plan to evaluate performance on a 2 week and 1-month forward basis and validate the effectiveness on these timescales as well. I understand that this approach limits upside potential in the reflected return figures, however, this simple approach will work in broad application across all transactions and allow the filtering of instantaneous moves which will provide a more robust model. 

Market information is also essential in analyzing the effectiveness of insider buying. If the market has been preforming well in the recent past, the purchase may just be due to market sentiment and optimism. However, if the purchase is large and flies in the face of market performance, there may be a chance an immediate, low beta move for the stock is imminent. To record this market action, percentage change figures are recorded for SPY and VIX in the 2-week and 1-month prior period are recorded relative to the trade data.

When we decide to act on the information is crucial. This is where the action date column comes in. Under US securities law, filing of a Sec form 4 has to occur within 2 days of the transaction. Often the filing will happen after hours and will require the information from the purchase to be priced in the following day. It is this next market open after filing where we will observe position return.

When working with market data as an individual, accuracy and availability of accurate and historical intra-day data is only available for an arm and a leg. Considering this, we will be using the opening and closing price where applicable to define performance in the past and returns in the future.
Grouped transactions for the same company are also something that seems relevant to seeking out alpha. If several company insiders, or the same insider, purchase large blocks of stock in quick succession, it would be foolish to not think this isn’t important.

After all these requirements and collected information, we must define our class threshold. Of course, since I am looking at both 2-week and 1-month returns, the class will change depending on which we want to analyze. However, the threshold return we are looking for is 7%. I don’t know why I picked this number. It seemed outsized enough in a short enough time period. 

With all these base considerations, the below head of the data frame is what we will be working with for our analysis. If you want to review the methods that went into collecting and organizing this information, take a look at the main method from the code base. 


# analysis
I know, it’s a lot to unpack… why don’t we start with some exploratory questions and see if we can’t find some alpha somewhere.
-	Average return, return distribution.
-	Class breakdown
-	Average return by filing quarter
-	Sectors with outsized return figures
-	Filing delay and return
-	Sector and return
-	Historical market performance and return
-	Volatility and return
-	Logistic regression
-	Feature engineering
Conclusions
Next steps

