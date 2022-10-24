import pandas as pd


class LogsProcess(object):
    def __init__(self, data):
        self.data = data
        self.account = self.data.Account.unique()
        if 'Robot' in self.data:
            self.robot = self.data.Robot.unique()
        else:
            self.data['Robot'] = 'Robot ' + self.data.shape[0]
            self.robot = self.data.Robot.unique()

    def df_finished(self):
        df = self.data
        finished = df[df['Status'].str.contains('Finished') & df['Status'].str.contains('\*FINALIZED\* a post')]
        finished.reset_index(drop=True, inplace=True)

        return finished
    
    def df_error(self):
        df = self.data
        error = df[df['Status'].str.contains('Error')].drop_duplicates('Status', ignore_index= True)
        error['Code'] = error['Status'].apply(lambda x: x.split(',')[0].split(':')[1].split('-')[0].replace(' ', ''))

        return error
    
    def df_total(self):
        finished = self.df_finished()
        error = self.df_error()
        total = pd.concat([finished, error], ignore_index=True)

        return total

    def count_finished_by_account(self):
        df = self.df_finished()
        count_finished = df.groupby(['Robot', 'Account']).Status.count().astype('int64')
        count_finished.rename('Finished Amount', inplace=True)
        
        return count_finished

    def count_error_by_account(self):
        df = self.df_error()
        count_error = df.groupby(['Robot', 'Account']).Status.count().astype('int64')
        count_error.rename('Error Amount', inplace=True)
        
        return count_error
    
    def count_total_by_account(self):
        df = self.df_total()
        count_total = df.groupby(['Robot', 'Account']).Status.count().astype('int64')
        count_total.rename('Total Amount', inplace=True)

        return count_total

    def count_error_code_by_account(self):
        df = self.df_error()
        count_error_code = df.groupby(['Robot', 'Account', 'Code']).Status.count().astype('int64')
        count_error_code.rename('Error Code Amount', inplace=True)
        
        return count_error_code

    def error_rate_by_account(self):
        error_count = self.count_error_by_account()
        total_count = self.count_total_by_account()
        error_rate = (error_count / total_count).fillna(0)
        error_rate.rename('error rate', inplace=True)
        
        return round(error_rate, 2)
    
    def error_distribution_by_account(self):
        code_error_count = self.count_error_code_by_account()
        code_errors_count = self.count_error_by_account()
        error_distribution = (code_error_count / code_errors_count).fillna(0)
        error_distribution.rename('Code Rate to Errors', inplace=True)
        
        return error_distribution
    
    def error_distribution_to_total_by_account(self):
        code_error_count = self.count_error_code_by_account()
        total_count = self.count_total_by_account()
        error_distribution = (code_error_count / total_count).fillna(0)
        error_distribution = error_distribution[error_distribution.index.dropna()]
        error_distribution.rename('Code Rate to Total', inplace=True)
        
        return error_distribution

    def count_grouped_by_account(self):
        count_finished = self.count_finished_by_account()
        count_error = self.count_error_by_account()
        count_total = self.count_total_by_account()

        df_list = [count_finished, count_error, count_total]
        
        df = pd.concat(df_list, axis=1).fillna(0)
        df.columns = ['Finished', 'Error', 'Total']
        df['Error Rate'] = df['Error'] / df['Total']
        
        return df
    
    def count_finished_by_robot(self):
        df = self.df_finished()
        count_finished = df.groupby(['Robot']).Status.count().astype('int64')
        count_finished.rename('Finished Amount', inplace=True)
        
        return count_finished

    def count_error_by_robot(self):
        df = self.df_error()
        count_error = df.groupby(['Robot']).Status.count().astype('int64')
        count_error.rename('Error Amount', inplace=True)
        
        return count_error
    
    def count_total_by_robot(self):
        df = self.df_total()
        count_total = df.groupby(['Robot']).Status.count().astype('int64')
        count_total.rename('Total Amount', inplace=True)
        
        return count_total

    def count_error_code_by_robot(self):
        df = self.df_error()
        count_error_code = df.groupby(['Robot', 'Code']).Status.count().astype('int64')
        count_error_code.rename('Error Code Amount', inplace=True)
        
        return count_error_code

    def error_rate_by_robot(self):
        error_count = self.count_error_by_robot()
        total_count = self.count_total_by_robot()
        error_rate = (error_count / total_count).fillna(0)
        error_rate.rename('Error Rate', inplace=True)
        
        return round(error_rate, 2)
    
    def error_distribution_by_robot(self):
        code_error_count = self.count_error_code_by_robot()
        code_errors_count = self.count_error_by_robot()
        error_distribution = (code_error_count / code_errors_count).fillna(0)
        error_distribution.rename('Code Rate to Errors', inplace=True)
        
        return error_distribution
    
    def error_distribution_to_total_by_robot(self):
        code_error_count = self.count_error_code_by_robot()
        total_count = self.count_total_by_robot()
        error_distribution = (code_error_count / total_count).fillna(0)
        error_distribution.rename('Code Rate to Total', inplace=True)
        
        return error_distribution
    
    def count_grouped_by_robot(self):
        count_finished = self.count_finished_by_robot()
        count_error = self.count_error_by_robot()
        count_total = self.count_total_by_robot()

        df_list = [count_finished, count_error, count_total]
        
        df = pd.concat(df_list, axis=1).fillna(0)
        df.columns = ['Finished', 'Error', 'Total']
        df['Error Rate'] = df['Error'] / df['Total']
        
        return df

    def filter_error_code(self, code):
        df = self.df_error().astype('str')
        
        return df[df['Code'] == code]

    def count_before_error(self, df, code):
        df = df.set_index('Date')
        df = df.sort_index()
        
        index = (df['Code'] == code).idxmax()
        df_code = df.loc[:index]
        count = df_code.shape[0] - 1
        
        return count

    
    
class GroupJoiner(LogsProcess):
    def __init__(self, path):
        super(GroupJoiner, self).__init__(path)
        self.activity = 'Group Joiner'

    def logs_related(self):
        df = self.data
        logs_related = df[(df['Status'].str.contains('Group Joiner')) & ~(df['Status'].isna())].drop_duplicates(['Status', 'Robot'])
        logs_related.reset_index(drop=True, inplace=True)

        return logs_related
        
    def df_finished(self):
        df = self.data
        finished = df[df['Status'].str.contains('Group Joiner') & df['Status'].str.contains('Finished operation')]
        finished.reset_index(drop=True, inplace=True)

        return finished
    
    def df_error(self):
        df = self.data
        error = df[df['Status'].str.contains('Group Joiner - Error')].drop_duplicates(['Status', 'Robot'])
        error['Code'] = error['Status'].apply(lambda x: x.split(':')[1].split('-')[0].replace(' ', ''))

        return error

    def df_specified_total(self, urls):
        df = self.logs_related()
        filtered_list = []
        for url in urls:
            filtered = df[df['Status'].str.contains(url) & ~(df['Status'].str.contains('Error'))]
            filtered['Url'] = url
            filtered_list.append(filtered)
        df_filtered = pd.concat(filtered_list, ignore_index=True)

        return df_filtered

    def df_specified_error(self, urls):
        df = self.df_error()
        filtered_list = []
        for url in urls:
            filtered = df[df['Status'].str.contains(url)]
            filtered['Url'] = url
            filtered_list.append(filtered)
        df_filtered = pd.concat(filtered_list, ignore_index=True)

        return df_filtered

    def count_specified_urls_total(self, urls):
        df = self.df_specified_total(urls)
        count_specified_urls_total = df.groupby(['Url']).Status.count().astype('int64')
        count_specified_urls_total.rename('Number of Total Url', inplace=True)

        return count_specified_urls_total

    def count_specified_urls_error(self, urls):
        df = self.df_specified_error(urls)
        count_specified_urls_error = df.groupby(['Url']).Status.count().astype('int64')
        count_specified_urls_error.rename('Number of Error Url', inplace=True)

        return count_specified_urls_error

    def count_specified_urls_total_by_robot(self, urls):
        df = self.df_specified_total(urls)
        count_specified_urls_total = df.groupby(['Url', 'Robot']).Status.count().astype('int64')
        count_specified_urls_total.rename('Number of Total Url Per Robot', inplace=True)

        return count_specified_urls_total

    def count_specified_urls_error_by_robot(self, urls):
        df = self.df_specified_error(urls)
        count_specified_urls_error = df.groupby(['Url', 'Robot']).Status.count().astype('int64')
        count_specified_urls_error.rename('Number of Error Url Per Robot', inplace=True)

        return count_specified_urls_error

    def count_specified_urls_total_by_account(self, urls):
        df = self.df_specified_total(urls)
        count_specified_urls_total = df.groupby(['Url', 'Robot', 'Account']).Status.count().astype('int64')
        count_specified_urls_total.rename('Number of Total Url Per Account', inplace=True)

        return count_specified_urls_total

    def count_specified_urls_error_by_account(self, urls):
        df = self.df_specified_error(urls)
        count_specified_urls_error = df.groupby(['Url', 'Robot', 'Account']).Status.count().astype('int64')
        count_specified_urls_error.rename('Number of Error Account', inplace=True)

        return count_specified_urls_error

    def count_specified_error_by_robot(self, urls):
        df = self.df_specified_error(urls)
        count_specified_error = df.groupby(['Robot']).Status.count().astype('int64')
        count_specified_error.rename('Error', inplace=True)

        return count_specified_error

    def count_specified_total_by_robot(self, urls):
        df = self.df_specified_total(urls)
        count_specified_total = df.groupby(['Robot']).Status.count().astype('int64')
        count_specified_total.rename('Total', inplace=True)

        return count_specified_total

    def count_specified_by_robot(self, urls):
        count_specified_error = self.count_specified_error_by_robot(urls)
        count_specified_total = self.count_specified_total_by_robot(urls)
        count_specified = pd.concat([count_specified_error, count_specified_total], axis=1, ignore_index=True).fillna(0).astype('int64')
        count_specified.columns = ['Error', 'Total']
        count_specified.insert(0, 'Finished', count_specified['Total'] - count_specified['Error'])
        count_specified['Success Rate'] = count_specified['Finished'] / count_specified['Total']

        return count_specified

    def count_specified_finished_by_robot(self, urls):
        count_specified = self.count_specified_by_robot(urls)
        count_specified_finished = count_specified['Finished']

        return count_specified_finished


    def count_specified_error_by_account(self, urls):
        df = self.df_specified_error(urls)
        count_specified_error = df.groupby(['Robot', 'Account']).Status.count().astype('int64')
        count_specified_error.rename('Error', inplace=True)

        return count_specified_error

    def count_specified_total_by_account(self, urls):
        df = self.df_specified_total(urls)
        count_specified_total = df.groupby(['Robot', 'Account']).Status.count().astype('int64')
        count_specified_total.rename('Total', inplace=True)

        return count_specified_total

    def count_specified_by_account(self, urls):
        count_specified_error = self.count_specified_error_by_account(urls)
        count_specified_total = self.count_specified_total_by_account(urls)
        count_specified = pd.concat([count_specified_error, count_specified_total], axis=1, ignore_index=True).fillna(0).astype('int64')
        count_specified.columns = ['Error', 'Total']
        count_specified.insert(0, 'Finished', count_specified['Total'] - count_specified['Error'])
        count_specified['Success Rate'] = count_specified['Finished'] / count_specified['Total']

        return count_specified

    def count_specified_finished_by_account(self, urls):
        count_specified = self.count_specified_by_account(urls)
        count_specified_finished = count_specified['Finished']

        return count_specified_finished




class Bump(LogsProcess):
    def __init__(self, path):
        super(Bump, self).__init__(path)
        self.activity = 'Bump'

    def df_finished(self):
        df = self.data
        finished = df[df['Status'].str.contains('Bump') & df['Status'].str.contains('Finished operation')]
        finished.reset_index(drop=True, inplace=True)

        return finished

    def df_error(self):
        df = self.data
        error = df[df['Status'].str.contains('Bump - Error')].drop_duplicates('Status', ignore_index=True)
        error['Code'] = error['Status'].apply(lambda x: x.split(':')[1].split('-')[0].replace(' ', ''))

        return error
    

class Publishing(LogsProcess):
    def __init__(self, path):
        super(Publishing, self).__init__(path)
        self.activity = 'Publishing'

    def df_finished(self):

        return print('df finished is included in df total.')
        
    def df_total(self):
        df = self.data
        total = df[df['Status'].str.contains('\*FINALIZED\* a post')].reset_index(drop=True)
        
        return total
    
    def df_error(self):
        df = self.data
        error = df[df['Status'].str.contains('Error publishing a Post')].reset_index(drop=True)
        error['Code'] = error['Status'].apply(lambda x: x.split(':')[1].split('-')[0].replace(' ', ''))
        
        return error

    def count_finished_by_account(self):
        count_total = self.count_total_by_account()
        count_error = self.count_error_by_account()
        count_finished = count_total.sub(count_error, fill_value=0).astype('int64')
        count_finished.rename('Finished Amount', inplace=True)

        return count_finished

    def count_finished_by_robot(self):
        count_total = self.count_total_by_robot()
        count_error = self.count_error_by_robot()
        count_finished = count_total.sub(count_error, fill_value=0).astype('int64')
        count_finished.rename('Finished Amount', inplace=True)

        return count_finished

    
class Tools(object):
    def __init__(self, data):
        self.data = data
        self.account = self.data.Account.unique()
        if 'Robot' in self.data.columns:
            self.robot = self.data.Robot.unique()
        else:
            self.data['Robot'] = 'Robot ' + self.data.shape[0]
            self.robot = self.data.Robot.unique()
        
    def group_joiner_publishing_concat_by_account(self):
        count_group_joiner_finished = GroupJoiner(self.data).count_finished_by_account()
        count_publishing_total = Publishing(self.data).count_total_by_account()
        count_concat = pd.concat([count_group_joiner_finished, count_publishing_total], axis=1).fillna(0)
        count_concat.columns = ['Number of Groups', 'Number of Destinations']
        count_concat['Destinations/Groups'] = count_concat.iloc[:, 1].div(count_concat.iloc[:, 0])
        
        return count_concat
    
    def group_joiner_publishing_concat_by_robot(self):
        count_group_joiner_finished = GroupJoiner(self.data).count_finished_by_robot()
        count_publishing_total = Publishing(self.data).count_total_by_robot()
        count_concat = pd.concat([count_group_joiner_finished, count_publishing_total], axis=1).fillna(0)
        count_concat.columns = ['Number of Groups', 'Number of Destinations']
        count_concat['Destinations/Groups'] = count_concat.iloc[:, 1].div(count_concat.iloc[:, 0])
        
        return count_concat

    def group_joiner_bump_concat_by_account(self):
        count_group_joiner_finished = GroupJoiner(self.data).count_finished_by_account()
        count_bump_finished = Bump(self.data).count_finished_by_account()
        count_concat = pd.concat([count_group_joiner_finished, count_bump_finished], axis=1).fillna(0)
        count_concat.columns = ['Number of Groups', 'Number of Bumps']
        count_concat['Bumps/Groups'] = count_concat.iloc[:, 1].div(count_concat.iloc[:, 0])

        return count_concat

    def group_joiner_bump_concat_by_robot(self):
        count_group_joiner_finished = GroupJoiner(self.data).count_finished_by_robot()
        count_bump_finished = Bump(self.data).count_finished_by_robot()
        count_concat = pd.concat([count_group_joiner_finished, count_bump_finished], axis=1).fillna(0)
        count_concat.columns = ['Number of Groups', 'Number of Bumps']
        count_concat['Bumps/Groups'] = count_concat.iloc[:, 1].div(count_concat.iloc[:, 0])

        return count_concat

    def publishing_bump_concat_by_account(self):
        count_publishing_total = Publishing(self.data).count_total_by_account()
        count_bump_finished = Bump(self.data).count_finished_by_account()
        count_concat = pd.concat([count_publishing_total, count_bump_finished], axis=1).fillna(0)
        count_concat.columns = ['Number of Publishing', 'Number of Bumps']
        count_concat['Bumps/Groups'] = count_concat.iloc[:, 1].div(count_concat.iloc[:, 0])

        return count_concat

    def publishing_bump_concat_by_robot(self):
        count_publishing_total = Publishing(self.data).count_total_by_robot()
        count_bump_finished = Bump(self.data).count_finished_by_robot()
        count_concat = pd.concat([count_publishing_total, count_bump_finished], axis=1).fillna(0)
        count_concat.columns = ['Number of Publishing', 'Number of Bumps']
        count_concat['Bumps/Publishing'] = count_concat.iloc[:, 1].div(count_concat.iloc[:, 0])

        return count_concat


def count_before_error(df, code):
    df = df.set_index('Date')
    df = df.sort_index()
    
    index = (df['Code'] == code).idxmax()
    df_code = df.loc[:index]
    count = df_code.shape[0] - 1
    
    return count



        