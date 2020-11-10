import pandas as pd
import Database
import datetime
import xlsxwriter


async def create_report(short_group: int) -> str:
    now = datetime.datetime.now()
    day, month, year = now.day, now.month, now.year
    att_list = await Database.get_all_attendance()
    try:
        fios = []
        groups = []
        dates = []
        for elem in att_list:
            group = elem[5]
            if int(group) // 100 != short_group:
                continue
            groups.append(group)
            fio = elem[4]
            fios.append(fio)
            date = str(elem[1]).zfill(2) + '.' + str(elem[2]).zfill(2) + '.' + str(elem[3])
            dates.append(date)

        df = pd.DataFrame(columns=['ФИО', 'Взвод'] + list(set(dates)))
        df['ФИО'] = fios
        df['Взвод'] = groups
        for elem in att_list:
            group = elem[5]
            if int(group) // 100 != short_group:
                continue
            fio = elem[4]
            date = str(elem[1]).zfill(2) + '.' + str(elem[2]).zfill(2) + '.' + str(elem[3])
            did_attend = elem[0]
            df.loc[(df['ФИО'] == fio) & (df['Взвод'] == int(group)), date] = did_attend

        df = df.drop_duplicates()
        df = df.fillna(0)
        df.to_excel(f"report_{day}_{month}_{year}.xlsx", index=False)
        print("Pandas success")
        print(df.info())
    except:
        print("Pandas exception")
        df = pd.DataFrame()
        df.to_excel(f"report_{day}_{month}_{year}.xlsx", index=False)

    return f"report_{day}_{month}_{year}.xlsx"


async def create_excel_report(short_group: int) -> str:
    now = datetime.datetime.now()
    day, month, year = now.day, now.month, now.year

    workbook = xlsxwriter.Workbook(f'записка_{day}_{month}_{year}.xlsx')
    worksheet = workbook.add_worksheet()

    att_list = await Database.get_all_attendance()
    try:
        fios_not_attended = []
        groups = []
        dates = []
        vzvod_size = 0
        for elem in att_list:
            print(elem)
            group = elem[5]
            if int(group) // 100 != short_group:
                continue
            if int(group) != 1911:  # TODO: delete
                continue
            if elem[1] != day or elem[2] != month or elem[3] != year:
                continue
            fio = elem[4]
            did_attend = elem[0]
            if not did_attend:
                fios_not_attended.append(fio)
            vzvod_size += 1
    except:
        print("Excel exception")
        return f'записка_{day}_{month}_{year}.xlsx'

    worksheet.write('A2', 'Cтроевая записка')
    worksheet.write('A3', 'Взвод №')
    worksheet.write('A4', 'По списку')
    worksheet.write('A5', 'В строю')
    worksheet.write('A6', 'Отсутствует')
    worksheet.write('A8', '№ пп')
    worksheet.write('A9', '1')
    worksheet.write('A10', '2')
    worksheet.write('A11', '3')
    worksheet.write('A12', '4')
    worksheet.write('A13', '5')
    worksheet.write('A15', 'Командир взвода')
    worksheet.write('A17', f'{day}.{month}.{year}')

    worksheet.write('B3', '1911')
    worksheet.write('B4', f'{vzvod_size}')
    worksheet.write('B5', f'{vzvod_size - len(fios_not_attended)}')
    worksheet.write('B6', f'{len(fios_not_attended)}')
    worksheet.write('B8', 'Фамилия инициалы')
    worksheet.write('B15', 'Студент Мельников')

    worksheet.write('C8', 'Причина неприбытия')

    for i in range(min(len(fios_not_attended), 5)):  # TODO: fix
        worksheet.write(f'B{9+i}', f'{fios_not_attended[i]}')

    workbook.close()

    return f'записка_{day}_{month}_{year}.xlsx'

if __name__ == "__main__":
    pass
