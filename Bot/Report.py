import pandas as pd
import Database
import datetime


async def create_report():
    att_list = await Database.get_all_attendance()
    fios = []
    groups = []
    dates = []
    for elem in att_list:
        date = str(elem[1]).zfill(2) + '.' + str(elem[2]).zfill(2) + '.' + str(elem[3])
        dates.append(date)
        fio = elem[4]
        fios.append(fio)
        group = elem[5]
        groups.append(group)

    df = pd.DataFrame(columns=['ФИО', 'Взвод'] + list(set(dates)))
    df['ФИО'] = fios
    df['Взвод'] = groups
    # TODO: don't save duplicates
    for elem in att_list:
        did_attend = elem[0]
        date = str(elem[1]).zfill(2) + '.' + str(elem[2]).zfill(2) + '.' + str(elem[3])
        fio = elem[4]
        group = elem[5]
        df.loc[(df['ФИО'] == fio) & (df['Взвод'] == int(group)), date] = did_attend
    now = datetime.datetime.now()
    day, month, year = now.day, now.month, now.year
    df = df.drop_duplicates()
    df = df.fillna(0)
    df.to_excel(f"report_{day}_{month}_{year}.xlsx", index=False)

if __name__ == "__main__":
    pass
