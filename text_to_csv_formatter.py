import pandas as pd
from streamlit_tools import *
from io import StringIO


def main():
    st.title('🎊Text File Convert CSV File App🎉')
    st.info('📤Please upload one file at least📤')
    uploaded_files = st.file_uploader('👇👇👇👇👇👇👇👇👇👇', accept_multiple_files=True)

    name_list = []
    df_list = []

    for file in uploaded_files:
        stringio = StringIO(file.getvalue().decode("utf-8"))
        data = stringio.read()
        name_list.append(file.name[:-4])
        df_list.append(data)
    data = pd.DataFrame({'txt文件名': name_list, '文本内容': df_list})

    st.download_button(
        label='📥Click on me to download the result📥',
        data=data.to_csv(index=False),
        file_name='result.csv',
        mime='txt/csv'
    )


if __name__ == '__main__':
    main()