#!/usr/bin/env python3

# performs a bootstrapping analysis comparing data from two different groups
def bootstrap_analysis_groups(df,group_1,group_2,measures,iterations=1000,sample_size=10,compare_measure='corr'):

    compare = 'corr'
    if compare_measure == 'ttest':
        compare = 'p-value'
        
    correlation = {}
    for meas in measures:
        correlation[meas] = []
        for i in range(0,iterations):
            group_1_df = df.loc[df['classID'] == group_1].sample(sample_size).reset_index(drop=True)
            group_2_df = df.loc[df['classID'] == group_2].sample(sample_size).reset_index(drop=True)

            if compare_measure == 'ttest':
                corr = ttest_ind(group_1_df[meas], group_2_df[meas],equal_var=False)[1]
            else:
                corr = np.corrcoef(group_1_df[meas].values.tolist(),group_2_df[meas].values.tolist())[0][1]
            correlation[meas].append(corr)

    corrs = pd.DataFrame()

    for meas in measures:
        corrs[meas+'_'+compare] = correlation[meas]
    corrs['iterations'] = [ f+1 for f in range(iterations) ]
    
    return corrs[['iterations']+[ f for f in corrs.keys().tolist() if f != 'iterations'] ]

# performs a bootstrapping analysis within two individual groups comparing between different measures
def bootstrap_analysis_within_groups(df,group_1,group_2,measures,iterations=1000,sample_size=10,compare_measure='corr'):

    compare = 'corr'
    if compare_measure == 'ttest':
        compare = 'p-value'

    group_1_corrs = {}
    group_2_corrs = {}
    for meas in range(len(measures)):
        for meas_2 in range(len(measures)):
            if measures[meas] != measures[meas_2]:
                measures_name = measures[meas]+'_'+measures[meas_2]
                inv_measures_name = measures[meas_2]+'_'+measures[meas]
                if measures_name not in list(group_1_corrs.keys()):
                    if inv_measures_name not in list(group_1_corrs.keys()):
                        group_1_corrs[measures_name] = []
                        group_2_corrs[measures_name] = []
                        for i in range(0,iterations):
                            group_1_df = df.loc[df['classID'] == group_1].sample(sample_size).reset_index(drop=True)
                            group_2_df = df.loc[df['classID'] == group_2].sample(sample_size).reset_index(drop=True)

                            if compare_measure == 'ttest':
                                corr_group_1 = ttest_ind(group_1_df[measures[meas]],group_1_df[measures[meas_2]],equal_var=False)[1]
                                corr_group_2 = ttest_ind(group_2_df[measures[meas]],group_2_df[measures[meas_2]],equal_var=False)[1]
                            else:
                                corr_group_1 = np.corrcoef(group_1_df[measures[meas]].values.tolist(),group_1_df[measures[meas_2]].values.tolist())[0][1]
                                corr_group_2 = np.corrcoef(group_2_df[measures[meas]].values.tolist(),group_2_df[measures[meas_2]].values.tolist())[0][1]
                            group_1_corrs[measures_name].append(corr_group_1)
                            group_2_corrs[measures_name].append(corr_group_2)

    corrs = pd.DataFrame()
    for meas in list(group_1_corrs.keys()):
        corrs[meas+'_'+compare] = group_1_corrs[meas] + group_2_corrs[meas]
        corrs['classID'] = [ group_1 for f in range(len(group_1_corrs[meas])) ] + [ group_2 for f in range(len(group_2_corrs[meas])) ]

    corrs['iterations'] = [ f+1 for f in range(0,iterations) ] + [ f+1 for f in range(0,iterations) ]
    return corrs[['classID','iterations']+[f for f in corrs.keys().tolist() if f != 'classID'] ]

# plots overall data
def plot_histogram(df,plot_measure,compare_measure,ax=''):
    
    if ax == '':
        sns.histplot(x=plot_measure,data=df,alpha=0.5)
        ax = plt.gca()
    else:
        sns.histplot(x=plot_measure,data=df,alpha=0.5,ax=ax)

    ax.vlines(x=df[plot_measure].mean(),ymin=0,ymax=ax.containers[1].datavalues.max(),linewidth=2,color='r')
    ax.text(x=df[plot_measure].max() * .4,y=ax.containers[1].datavalues.max() *.75,s='average '+compare_measure+': %s' %(str('{:0.3e}'.format(df[plot_measure].mean()))))
    
# plots individual group data
def plot_histogram_groups(df,plot_measure,palette='',ax=''):

    if ax == '':
        if palette != '':
            sns.histplot(x=plot_measure,hue='classID',data=df,palette=palette,alpha=0.25)
        else:
            sns.histplot(x=plot_measure,hue='classID',data=df,alpha=0.25)
        ax = plt.gca()
    else:
        if palette != '':
            sns.histplot(x=plot_measure,hue='classID',data=df,palette=palette,alpha=0.25,ax=ax)
        else:
            sns.histplot(x=plot_measure,hue='classID',data=df,alpha=0.25,ax=ax)

    if palette:
        ax.vlines(x=df.loc[df['classID'] == group_1].mean()[plot_measure],ymin=0,ymax=ax.containers[1].datavalues.max(),color=palette[group_1])
        ax.vlines(x=df.loc[df['classID'] == group_2].mean()[plot_measure],ymin=0,ymax=ax.containers[0].datavalues.max(),color=palette[group_2])
    else:
        ax.vlines(x=df.loc[df['classID'] == group_1].mean()[plot_measure],ymin=0,ymax=ax.containers[1].datavalues.max(),color='r')
        ax.vlines(x=df.loc[df['classID'] == group_2].mean()[plot_measure],ymin=0,ymax=ax.containers[0].datavalues.max(),color='g')

# simple function to compute the number of columns and rows needed based on number of measures and having an n x 3 style figure layout
def set_up_figure(measures):
    number_measures = int(len(measures))
    if number_measures < 3:
        num_rows = 1
    else:
        num_rows = int(np.floor(number_measures / 3))
        if number_measures % 3 > 0:
            num_rows = num_rows +1
    
    if num_rows > 1:
        total_columns = 3
    else:
        total_columns = (number_measures %3)
        if number_measures % 3 == 0:
            total_columns = 3

    return num_rows,total_columns


if __name__ == "__main__":
    main()