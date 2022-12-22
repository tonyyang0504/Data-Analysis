import os.path

import streamlit_tools
from streamlit_tools import *
from tools import split_csv_by_rows, compress_file, delete_files_and_subdirs
import zipfile


df = pd.read_csv('./group members/new files/2.csv')
save_dir = './group members/splited_csv_files'
unit_no = 2500

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

split_csv_by_rows(df, unit_no, save_dir)
compress_file(save_dir)
delete_files_and_subdirs(save_dir)


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

