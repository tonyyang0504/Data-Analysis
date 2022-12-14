import pandas as pd
from streamlit_tools import *
from io import StringIO


def main():
    st.title('๐Text File Convert CSV File App๐')
    st.info('๐คPlease upload one file at least๐ค')
    uploaded_files = st.file_uploader('๐๐๐๐๐๐๐๐๐๐', accept_multiple_files=True)

    name_list = []
    df_list = []

    for file in uploaded_files:
        stringio = StringIO(file.getvalue().decode("utf-8"))
        data = stringio.read()
        name_list.append(file.name[:-4])
        df_list.append(data)
    data = pd.DataFrame({'txtๆไปถๅ': name_list, 'ๆๆฌๅๅฎน': df_list})

    st.download_button(
        label='๐ฅClick on me to download the result๐ฅ',
        data=data.to_csv(index=False),
        file_name='result.csv',
        mime='txt/csv'
    )


if __name__ == '__main__':
    main()