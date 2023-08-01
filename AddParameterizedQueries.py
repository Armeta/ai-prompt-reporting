import json
import pyodbc

f = open('json\\answerKey.json','r')
key = json.load(f)
f.close()
f = open('json\\QueryOptions.json','r')
options = json.load(f)
f.close()

pagesTables = {'sales-retail':'[DASHBOARD].[STORY_RETAIL_SALES_ANALYSIS]',
             'sales-opportunity':'[DASHBOARD].[STORY_SALES_ACCELERATOR]',
             'sales-compare':'[DASHBOARD].[STORY_RETAIL_SALES_ANALYSIS]',
             'sales-digital':'[DASHBOARD].[STORY_DIGITAL_ANALYSIS]',
             'analysis-product':'[DASHBOARD].[STORY_PRODUCT_INSIGHT]',
             'location-review':'[DASHBOARD].[STORY_LOCATION_REVIEW]',
             'top-styles':'[DASHBOARD].[STORY_PRODUCT_STORYBOARD]'}

pagesDesc = {'sales-retail':'Analysis of sales data showing ',
             'sales-opportunity':'Potential sales opportunity ',
             'sales-compare':'Comparing revenue, item on hand cost, item on hand value, and item on hand units against each other ',
             'sales-digital':'Digital website metrics, such as conversion rate and average order value by site ',
             'analysis-product':'Insight on how certain products are selling ',
             'location-review':'Sales and inventory for specific locations and stores ',
             'top-styles':'Highlighting the top products at a specified location '}

prefixes = ['What was the ', 'What are the ', 'What is the ', 'What\'s the', 'Whats the ', 'What are ', 'What ', 'How are the ', 'How often do ', 'How many ', 'How does ', 'How do ', 'I need to ', 'Show me ', 'Which ']
prefixes = [prefix.lower() for prefix in prefixes]

count = 0
for pair in key['pairs']:
    if(pair['ans'][:5] == 'https'):
        if(pair['ans'].find('?') > 0):
            page = pair['ans'][37:pair['ans'].find('?')]
        else:
            page = pair['ans'][37:]
        pageDesc = pagesDesc[page]
        pageTable = pagesTables[page]

        prompt = pair['prompt'].lower()

        promptDesc = ''
        for prefix in prefixes:
            if(prompt.find(prefix) == 0):
                promptDesc = pageDesc + (prompt.replace(prefix, '').replace('?', '.'))
                break
        if(promptDesc == ''):
            #print(prompt)
            1
        else:
            promptQuery = ''
            if(prompt.find('what are the top-selling products ') > -1):
                dollars = False if prompt.find(' units') >= 0 else True
                month = True if prompt.find(' month') >= 0 else False
                thisWeek = False if prompt.find(' last week') >= 0 else True
                family = 'OTHER' if prompt.find(' other') >= 0 else 'MENS' if prompt.find(' men') >= 0 else 'WOMENS' if prompt.find(' women') >= 0 else 'JUNIORS' if prompt.find(' junior') >= 0 else 'CHILDRENS' if prompt.find(' child') >= 0 else 'COSMETICS' if prompt.find(' cosmetic') >= 0 else 'ACCESSORIES' if (prompt.find(' accessories') >= 0 or prompt.find(' accessory') >= 0) else 'SHOES' if prompt.find(' shoe') >= 0 else 'HOME' if prompt.find(' home') >= 0 else None
                location = 'ROCKVILLE,MD' if prompt.find(' rockville') >= 0 else 'MIDDLETOWN,WV' if prompt.find(' middletown') >= 0 else 'PITTSBURGH,PA' if prompt.find(' pittsburgh') >= 0 else 'HERSHEY,PA' if prompt.find(' hershey') >= 0 else 'LANCASTER,PA' if prompt.find(' lancaster') >= 0 else 'WILLIAMSPORT,PA' if prompt.find(' williamsport') >= 0 else 'NEWORLEANS,LA' if prompt.find(' neworleans') >= 0 else 'SYRACUSE,NY' if prompt.find(' syracuse') >= 0 else 'BATONROUGE,LA' if prompt.find(' batonrouge') >= 0 else 'BIRMINGHAM,AL' if prompt.find(' birmingham') >= 0 else 'PHILADELPHIA,PA' if prompt.find(' philadelphia') >= 0 else 'HUNTSVILLE,AL' if prompt.find(' huntsville') >= 0 else 'YORK,PA' if prompt.find(' york') >= 0 else 'KNOXVILLE,TN' if prompt.find(' knoxville') >= 0 else 'MEMPHIS,TN' if prompt.find(' memphis') >= 0 else 'SCHENECTADY,NY' if prompt.find(' schenectady') >= 0 else 'JACKSON,MI' if prompt.find(' jackson') >= 0 else 'BILOXI,MI' if prompt.find(' biloxi') >= 0 else 'FLAGSTAFF,AZ' if prompt.find(' flagstaff') >= 0 else 'PHOENIX,AZ' if prompt.find(' phoenix') >= 0 else 'SAN FRANSICO,CA' if prompt.find(' san fransico') >= 0 else 'BANGOR,ME' if prompt.find(' bangor') >= 0 else 'DALLAS,TX' if prompt.find(' dallas') >= 0 else 'PORTLAND,ME' if prompt.find(' portland') >= 0 else 'MANCHESTER ,NH' if prompt.find(' manchester ') >= 0 else 'WILTON,NY' if prompt.find(' wilton') >= 0 else 'BRICK,NJ' if prompt.find(' brick') >= 0 else 'HAMDEN,CT' if prompt.find(' hamden') >= 0 else 'BURLNGTON,VT' if prompt.find(' burlngton') >= 0 else 'CONCORD,NH' if prompt.find(' concord') >= 0 else 'LEXINGTON,MA' if prompt.find(' lexington') >= 0 else 'HARTFORD,CT' if prompt.find(' hartford') >= 0 else 'NORFOLK,NE' if prompt.find(' norfolk') >= 0 else 'HOUSTON,TX' if prompt.find(' houston') >= 0 else 'HASTINGS,NE' if prompt.find(' hastings') >= 0 else 'SEATTLE,WA' if prompt.find(' seattle') >= 0 else 'TACOMA,WA' if prompt.find(' tacoma') >= 0 else 'AUSTIN,TX' if prompt.find(' austin') >= 0 else 'OLYMPIA,WA' if prompt.find(' olympia') >= 0 else 'PORTLAND,OR' if prompt.find(' portland') >= 0 else 'EUGENE,OR' if prompt.find(' eugene') >= 0 else 'SANANTONIO,TX' if prompt.find(' sanantonio') >= 0 else 'FORTWORTH,TX' if prompt.find(' fortworth') >= 0 else 'PLANO,TX' if prompt.find(' plano') >= 0 else 'ELPASO,TX' if prompt.find(' elpaso') >= 0 else 'AMARILLO,TX ' if prompt.find(' amarillo') >= 0 else 'LAREDO,TX' if prompt.find(' laredo') >= 0 else 'WACO,TX' if prompt.find(' waco') >= 0 else 'HONEYCRK,IN' if prompt.find(' honeycrk') >= 0 else 'PADUCAH,KY' if prompt.find(' paducah') >= 0 else 'COLUMBUS,IN' if prompt.find(' columbus') >= 0 else 'MUNCIE,IN' if prompt.find(' muncie') >= 0 else 'KOKOMO,IN' if prompt.find(' kokomo') >= 0 else 'BLOOMNGTN,IL' if prompt.find(' bloomngtn') >= 0 else 'PERU,IL' if prompt.find(' peru') >= 0 else 'GRT FALLS,MT' if prompt.find(' grt falls') >= 0 else 'RAPIDCITY,SD' if prompt.find(' rapidcity') >= 0 else 'ROCKSPRNG,WY' if prompt.find(' rocksprng') >= 0 else 'TUCSON,AZ' if prompt.find(' tucson') >= 0 else 'SAN JOSE,CA' if prompt.find(' san jose') >= 0 else 'LOS ANGELES,CA' if prompt.find(' los angeles') >= 0 else 'SAN DIEGO,CA' if prompt.find(' san diego') >= 0 else 'EUREKA,CA' if prompt.find(' eureka') >= 0 else 'ATLANTA,GA' if prompt.find(' atlanta') >= 0 else 'MACON,GA' if prompt.find(' macon') >= 0 else 'FRESNO,CA' if prompt.find(' fresno') >= 0 else 'REDDING,CA' if prompt.find(' redding') >= 0 else 'SAN BERNARDINO,CA' if prompt.find(' san bernardino') >= 0 else 'CHARLESTON,SC' if prompt.find(' charleston') >= 0 else None
                #district
                promptQuery = 'SELECT TOP 1 CONCAT(BRAND_LABEL, \' \', ISN_DESC, \' (\',  CATEGORY_LABEL, \') is a top selling %s product%s%s with %s.\') FROM [DASHBOARD].[STORY_PRODUCT_STORYBOARD] F JOIN [STORY].[LKP_BRAND] B ON B.BRAND_CD = F.BRAND_CD JOIN [STORY].[LKP_CATEGORY] C ON C.CATEGORY_CD = F.CATEGORY_CD JOIN [STORY].[LKP_DEPARTMENT] D ON D.DEPARTMENT_CD = F.DEPARTMENT_CD JOIN [STORY].[LKP_PRODUCT_FAMILY] P ON P.PRODUCT_FAMILY_CD = D.PRODUCT_FAMILY_CD JOIN [STORY].[LKP_LOCATION] L ON L.LOCATION_CD = F.LOCATION_CD JOIN [STORY].[LKP_DISTRICT] DI ON DI.DISTRICT_CD = L.DISTRICT_CD WHERE TIMEFRAME=\'%s\' AND ISN_IMAGE_URL IS NOT NULL AND UNIT_TYPE=\'%s\'%s%s ORDER BY %s DESC;' % (family.lower() if family else '\', PRODUCT_FAMILY_LABEL, \'', ' this month' if month else ' this week', ' in \' , LOCATION_LABEL, \'' if location else '', '$\', NET_SALES_DOLLARS_TY, \' of revenue' if dollars else '\', NET_SALES_UNITS_TY, \' units sold', ('TW' if thisWeek else 'LW')+('MTD' if month else 'WTD'), 'DOLLARS' if dollars else 'UNITS', ' AND PRODUCT_FAMILY_LABEL=\''+family+'\'' if family else '', ' AND LOCATION_LABEL=\''+location+'\'' if location else '', 'NET_SALES_DOLLARS_TY' if dollars else 'NET_SALES_UNITS_TY')
            if(promptQuery == ''):
                #print(prompt)
                1
            else:
                #print(promptQuery)
                options['options'].append({'type': 'query','query': promptQuery, 'result':None, 'desc': promptDesc, 'encoding':None})
                count += 1

f = open('json\\QueryOptions.json','w')
f.write(json.dumps(options).replace('{', '\n{').replace('",', '",\n').replace('"}', '"\n}'))
f.close()

print('Added %d options' % (count))


