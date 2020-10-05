import pandas as pd
import Database
import datetime


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

if __name__ == "__main__":
    pass
