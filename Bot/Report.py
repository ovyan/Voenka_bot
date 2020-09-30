import pandas as pd
import Database


async def create_report():
    att_list = await Database.get_all_attendance()
    fios = []
    groups = []
    dates = []
    for elem in att_list:
        date = str(elem[1]) + '.' + str(elem[2]) + '.' + str(elem[3])
        dates.append(date)
        fio = elem[4]
        fios.append(fio)
        group = elem[5]
        groups.append(group)

    df = pd.DataFrame(columns=['ФИО', 'Взвод'] + list(set(dates)))
    df['ФИО'] = fios
    df['Взвод'] = groups
    for elem in att_list:
        did_attend = elem[0]
        date = str(elem[1]) + '.' + str(elem[2]) + '.' + str(elem[3])
        fio = elem[4]
        group = elem[5]
        df.loc[(df['ФИО'] == fio) & (df['Взвод'] == int(group)), date] = did_attend

    df.to_excel("report.xlsx", index=False)

if __name__ == "__main__":
    pass
