import os.path

import streamlit_tools
from streamlit_tools import *
from tools import split_csv_by_rows, compress_files, delete_files_and_subdirs
import zipfile


df = pd.read_csv('./group members/new files/2.csv')
save_dir = './group members/splited_csv_files'
unit_no = 2500

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

split_csv_by_rows(df, unit_no, save_dir)
compress_files(save_dir)
delete_files_and_subdirs(save_dir)


def main(unit_no):
    st.title('๐Split CSV File By Rows App๐')
    st.info('๐คPlease upload one file at least๐ค')
    st.number_input(unit_no)
    uploaded_files = st.file_uploader('๐๐๐๐๐๐๐๐๐๐', accept_multiple_files=True)
    if uploaded_files:
        df_list = []
        for file in uploaded_files:
            df = pd.read_csv(file)
            df_list.append(df)
        df = pd.concat(df_list, ignore_index=True)
        if len(df_list) > 1:
            st.success(f'๐You have uploaded {len(df_list)} files successfully.๐')
        else:
            st.success(f'๐You have uploaded {len(df_list)} file successfully.๐')
        return df
    else:
        st.error('๐ฅPlease upload one file at least to continue๐ฅ')
        st.stop()

