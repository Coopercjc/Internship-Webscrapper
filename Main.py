import mechanicalsoup
import csv
b1 = mechanicalsoup.StatefulBrowser()
b2 = mechanicalsoup.StatefulBrowser()
b3 = mechanicalsoup.StatefulBrowser()
b1.open('https://mms.mckesson.com/sm/catalog.mck?c=0')
b1.select_form()
b1['userName'] = '########'
b1['password'] = '########'
b1.submit_selected()
b1.select_form()
b1.submit_selected()
b2.open('https://mfimedical.com/')
b3.open('https://www.boundtree.com/login')
b3.select_form('#loginForm')
b3['j_username'] = '##########'
b3['j_password'] = '##########'
b3.submit_selected()
with open('testoutput.csv', 'w') as output:
    writer = csv.writer(output, delimiter=',', lineterminator="\n")
    with open('test.csv', 'r', encoding='utf-8-sig') as input:
        reader = csv.reader(input)
        count = 1
        for row in reader:
            prices = []
            prodID = []
            b1.open('https://mms.mckesson.com/sm/catalog.mck?c=0')
            print('Iteration #' + str(count))
            print('Product ID: ' + str(row[0]))

            count += 1
            if count == 50:
                break
            prodID.append(row)

            b1.select_form('#fsearch')
            b1['q'] = row
            b1.submit_selected()

            b2.select_form('form[action="/search"]')
            b2['q'] = row
            b2.submit_selected()

            b3.select_form('form[action="/search/"]')
            b3['text'] = row
            b3.submit_selected()

            prices.append(row[0])

            #MCKESSON
            one = str(b1.get_current_page().find_all(string='No Further Refinements'))
            if one != '[]':
                lin = str(b1.get_current_page().find_all(class_='item-description'))
                idx = lin.find('a href="')
                lin = lin[idx + 8:]
                end = lin.find('"')
                lin = lin[:end]
                url = "https://mms.mckesson.com/sm/" + lin
                b1.open(url)
            change = str(b1.get_current_page().find_all('b', string=('PSS  Item #' + str(row[0]))))
            result = str(b1.get_current_page().find_all(string='No Products Matched Your Criteria'))
            if change != '[]' and result == '[]':
                prod= str(b1.get_current_page().find_all(class_="gray itemnumber"))
                idx = prod.find('#')
                prod = prod[idx + 1:]
                idx = prod.find('<')
                prod = prod[:idx]
                url = "https://mms.mckesson.com/sm/catalog.item.mck?id=" + prod + "&src=PC"
                b1.open(url)
            multiple = str(b1.get_current_page().find_all(string='Narrow Your Results'))
            if result != '[]':
                prices.append('ERROR-Not Found')
                b1.open('https://mms.mckesson.com/sm/catalog.mck?c=0')
            elif multiple != '[]':
                prod = str(b1.get_current_page().find_all(class_="gray itemnumber"))
                idx = prod.find('#')
                prod = prod[idx + 1:]
                idx = prod.find('<')
                prod = prod[:idx]
                if prod == str(row[0]):
                    url = "https://mms.mckesson.com/sm/catalog.item.mck?id=" + prod + "&src=PC"
                    b1.open(url)
                    uom = str(b1.get_current_page().find_all('p'))
                    price = uom.find('</b>')
                    uom = uom[price + 5:]
                    dot = uom.find('</p')
                    prices.append(uom[:dot])
                else:
                    prices.append('ERROR-Multiple Found')
                    b1.open('https://mms.mckesson.com/sm/catalog.mck?c=0')
            else:
                uom = str(b1.get_current_page().find_all('p'))
                price = uom.find('</b>')
                uom = uom[price + 5:]
                dot = uom.find('</p')
                prices.append(uom[:dot])


            '''#MFIMEDICAL
            result = str(b2.get_current_page().find_all(string='No results found'))
            if result != '[]':
                prices.append('ERROR-Not Found')
                b2.open('https://mfimedical.com/')
            multiple = str(b2.get_current_page().find_all(string='Narrow Your Results'))
            if multiple != '[]':
                prices.append('ERROR-Multiple Found')
                b2.open('https://mfimedical.com/')'''


            #BOUNDTREE
            result = str(b3.get_current_page().find_all(string="Sorry, we couldn't find any results for your search"))
            multiple = str(b3.get_current_page().find_all(string='Products Per Page:'))
            if result != '[]':
                prices.append('ERROR-Not Found')
                b3.open('https://www.boundtree.com/')
            elif multiple != '[]':
                html = str(b3.get_current_page())
                start = html.find('class="product__listing product__list"')
                html = html[start:]
                if html.find(str('>' + row[0]) + ',') == -1 or html.find(',' + str(row[0]) + ',') == -1 or html.find(',' + str(row[0]) + '<') == -1:
                    prices.append('ERROR-Multi')
                else:
                    html = html[html.find(str(row[0]) + '</div'):]
                    html = html[html.find('List Price:'):]
                    price = html[html.find('$'): html.find('.') + 3]
                    prices.append(price)
            else:
                uom = str(b3.get_current_page().find_all(id='priceForUnit'))
                price = uom.find('>')
                uom = uom[price + 1:]
                dot = uom.find('</')
                prices.append(uom[:dot] + ' Check price')
            writer.writerow(prices)
b1.close()
b2.close()
b3.close()
output.close()
input.close()

