import os.path

import streamlit_tools
from streamlit_tools import *
from tools import split_csv_by_rows
import zipfile


df = pd.read_csv('./group members/new files/1.csv')
save_dir = './group members/splited_csv_files'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
unit_no = 2500
split_csv_by_rows(df, unit_no, save_dir)

z = zipfile.ZipFile('zipfiles.zip', 'w', zipfile.ZIP_DEFLATED)
for file in os.listdir(save_dir):
    z.write(os.path.join(save_dir, file))
z.close()


def main(unit_no):
    st.title('🎊Split CSV File By Rows App🎉')
    st.info('📤Please upload one file at least📤')
    st.number_input(unit_no)
    uploaded_files = st.file_uploader('👇👇👇👇👇👇👇👇👇👇', accept_multiple_files=True)
    if uploaded_files:
        df_list = []
        for file in uploaded_files:
            df = pd.read_csv(file)
            df_list.append(df)
        df = pd.concat(df_list, ignore_index=True)
        if len(df_list) > 1:
            st.success(f'👏You have uploaded {len(df_list)} files successfully.👏')
        else:
            st.success(f'👏You have uploaded {len(df_list)} file successfully.👏')
        return df
    else:
        st.error('💥Please upload one file at least to continue💥')
        st.stop()

