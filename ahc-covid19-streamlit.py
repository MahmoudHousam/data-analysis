import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# preview & clean
st.title("AHC COVID19")
DATE_COLUMN = "date_of_1st_positive_or_suspected__result"
DATA_URL = "ahc-covid-19.csv"


def getDepartment(dep):
    if "nurse" in dep or "aicu hn" in dep or "cathlab hn" in dep or "aw na" in dep:
        return "Nurse"
    elif "doctor" in dep or "perfesionist" in dep or "cardiology" in dep:
        return "Doctor"
    elif "admin" in dep or "reception" in dep:
        return "Admin"
    else:
        return "Other"


@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_csv(DATA_URL)
    #clean columns name
    lowercase = lambda x: str(x).lower().strip().replace(" ", "_")
    df.rename(lowercase, axis="columns", inplace=True)

    #clean data lowercase and remove whitespace
    df[["dept.",
        "result",
        "symptoms",
        "isolation",
        "status"]] = df[["dept.",
                        "result",
                        "symptoms",
                        "isolation",
                        "status"]].apply(lambda x : x.str.lower().str.strip())

    #clean data replace wrong data entry
    df['dept.'].replace('cathlab nurse','cath lab nurse',inplace=True)
    df['dept.'].replace('cath lab nurse aid','cath-lab nurse aid',inplace=True)
    df['dept.'].replace(['picu staff','picu nurse'],'picu staff nurse',inplace=True)
    df['dept.'].replace(['nurse aid aicu'],'aicu nurse aid',inplace=True)
    df['dept.'].replace(['aicu nurse'],'aicu staff nurse',inplace=True)
    df['dept.'].replace(['ccu nurse-aid'],'ccu nurse aid',inplace=True)
    df['dept.'].replace(['hk','houssing'],'houskeeping',inplace=True)

    df["result"].replace(["follow up after 14 days positve",
                            "posirive"],
                        "positive",
                         inplace=True)
    df["isolation"].replace("home", "home isolation",inplace=True)

    df["department"] = df["dept."].apply(getDepartment)
    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN])
    return df


df = load_data()
df.columns
st.write(df.head())

# Dates
st.write("dates needs clean step")
timeline = df[DATE_COLUMN].value_counts()
timeline

# Deps
st.write("# Departments")
depx = df["dept."].value_counts()
depx

dep = df["department"].value_counts().reset_index()
dep

data = [
    go.Pie(
        labels=dep["index"],
        values=dep.department,
        textposition="inside",
        textinfo="value+percent",
        direction="clockwise",
        sort=False,
    )
]
layout = go.Layout(title="Departments")
fig = go.Figure(data, layout)
st.plotly_chart(fig)

# Top 5 positive sub Department
st.subheader('Top 5 positive sub Department')

dept = df[df['result']=='positive']['dept.'].value_counts()
dept
dept_pie = dept.nlargest(5)
dept_pie
data = [
    go.Pie(
        labels=dept_pie.index,
        values=dept_pie.values,
        textposition="inside",
        textinfo="value+percent",
        direction="clockwise",
        sort=False,
    )
]
layout = go.Layout(title="Top 5 positive sub Department")
fig = go.Figure(data, layout)
st.plotly_chart(fig)
# all positive Department count

data =[go.Bar(x=dept.index,
                y=dept.values,
                text=dept.values,
                textposition='auto')]
fig = go.Figure(data)
fig.update_layout(title_text='Positive Departments')
st.plotly_chart(fig)



# Symptoms
st.write("# Symptoms")
symps = df["symptoms"].value_counts().reset_index()
symps


data = [
    go.Pie(
        labels=symps["index"],
        values=symps["symptoms"],
        textposition="inside",
        textinfo="value+percent",
        direction="clockwise",
        sort=False,
    )
]
layout = go.Layout(title="Symptoms")
fig = go.Figure(data, layout)
st.plotly_chart(fig)

st.write("# Department symptoms")
depsep = df.groupby("department")["symptoms"].value_counts().unstack().fillna(0)
depsep

fig = go.Figure(
    data=go.Heatmap(
        z=depsep.values,
        x=depsep.index,
        y=depsep.columns,
        hoverongaps=False,
        colorscale="reds",
    )
)
st.plotly_chart(fig)

# symptoms
df['symptoms'].value_counts()

symptoms = df[['id',
                'result',
                'symptoms']].groupby(by=['result',
                                        'symptoms']).count().reset_index()
symptoms

positive_x=symptoms[symptoms['result']=='positive']['symptoms'].values
positive_y=symptoms[symptoms['result']=='positive']['id'].values

suspected_x=symptoms[symptoms['result']=='suspected']['symptoms'].values
suspected_y=symptoms[symptoms['result']=='suspected']['id'].values

#Result and symptoms
data =[go.Bar(name='Positive',
                x=positive_x,
                y=positive_y,
                text=positive_y,
                textposition='auto'),
      go.Bar(name='Suspected',
            x=suspected_x,
            y=suspected_y,
            text=suspected_y,
            textposition='auto')]

fig = go.Figure(data)
fig.update_layout(title_text='Positive & Suspected symptoms ')
st.plotly_chart(fig)




# Results
st.write("# Results")
results = df["result"].value_counts().reset_index()
results


data = [
    go.Pie(
        labels=results["index"],
        values=results["result"],
        textposition="inside",
        textinfo="value+percent",
        direction="clockwise",
        sort=False,
    )
]
layout = go.Layout(title="Results")
fig = go.Figure(data, layout)
st.plotly_chart(fig)


# Isolation
st.subheader("Isolation")
isolation = df["isolation"].value_counts().reset_index()
isolation

data = [
    go.Pie(
        labels=isolation["index"],
        values=isolation["isolation"],
        textposition="inside",
        textinfo="value+percent",
        direction="clockwise",
        sort=False,
    )
]
layout = go.Layout(title="Isolation")
fig = go.Figure(data, layout)
st.plotly_chart(fig)

st.write("# Currently Isolated")
isolation = (
    df[df["status"] == "still isolated"]["isolation"].value_counts().reset_index()
)
isolation


data = [
    go.Pie(
        labels=isolation["index"],
        values=isolation["isolation"],
        textposition="inside",
        textinfo="value+percent",
        direction="clockwise",
        sort=False,
    )
]
layout = go.Layout(title="Isolation")
fig = go.Figure(data, layout)
st.plotly_chart(fig)

#Result and Isolation
st.subheader('Positive & Suspected Isolation')
isolation = df[['id','result','isolation']].groupby(by=['result','isolation']).count().reset_index()
isolation

positive_x=isolation[isolation['result']=='positive']['isolation'].values
positive_y=isolation[isolation['result']=='positive']['id'].values

suspected_x=isolation[isolation['result']=='suspected']['isolation'].values
suspected_y=isolation[isolation['result']=='suspected']['id'].values

data =[go.Bar(name='Positive',
                x=positive_x,
                y=positive_y,
                text=positive_y,
                textposition='auto'),
      go.Bar(name='Suspected',
                x=suspected_x,
                y=suspected_y,
                text=suspected_y,
                textposition='auto')]

fig = go.Figure(data)
fig.update_layout(title_text='Positive & Suspected Isolation')
st.plotly_chart(fig)


# Status
st.subheader("# Status")
status = df["status"].value_counts().reset_index()
status


data = [
    go.Pie(
        labels=status["index"],
        values=status["status"],
        textposition="inside",
        textinfo="value+percent",
        direction="clockwise",
        sort=False,
    )
]
layout = go.Layout(title="Status")
fig = go.Figure(data, layout)
st.plotly_chart(fig)
st.write("# Positive Cases Current Status")
posstatus = df[df["result"] == "positive"]["status"].value_counts().reset_index()
posstatus


data = [
    go.Pie(
        labels=posstatus["index"],
        values=posstatus["status"],
        textposition="inside",
        textinfo="value+percent",
        direction="clockwise",
        sort=False,
    )
]
layout = go.Layout(title="Status")
fig = go.Figure(data, layout)
st.plotly_chart(fig)


status = df[['id',
            'result',
            'status']].groupby(by=['result',
                                    'status']).count().reset_index()
status

positive_x=status[status['result']=='positive']['status'].values
positive_y=status[status['result']=='positive']['id'].values

# %%
suspected_x=status[status['result']=='suspected']['status'].values
suspected_y=status[status['result']=='suspected']['id'].values

# %%
#Result and Isolation
data =[go.Bar(name='Positive',
            x=positive_x,
            y=positive_y,
            text=positive_y,
            textposition='auto'),
      go.Bar(name='Suspected',
                x=suspected_x,
                y=suspected_y,
                text=suspected_y,
                textposition='auto')]
fig = go.Figure(data)
fig.update_layout(title_text='esult and Isolation')
st.plotly_chart(fig)


def clean_date(x):
    try:
         return pd.to_datetime(x[0] ,
                    errors='coerce',
                     format="%d/%m/%Y").date()
    except :
        return None

df['date_of_1st_follow_up']
follow = df['date_of_1st_follow_up'].str.split()
follow = follow.apply(clean_date )
follow

#date of postitive
st.subheader('Date of positive')
df[DATE_COLUMN]
data=[go.Box(name='Positive number',
                y=df[DATE_COLUMN]),
      go.Box(name='1st follow',
                    y=follow)]
fig = go.Figure(data)
fig.update_layout(title_text='Date of positive')
st.plotly_chart(fig)


timeline
data =[go.Bar(name='date of Positive',
            x=timeline.index,
            y=timeline,
            text=timeline,
            textposition='auto')]

fig = go.Figure(data)
fig.update_layout(title_text='Data of Positive')
st.plotly_chart(fig)


tracing = df['tracing'].value_counts()
tracing
st.write(df.head())
