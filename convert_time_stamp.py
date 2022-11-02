# %%
import pandas as pd


# %%
df_player = pd.read_csv("player_data_pp_P1_original.csv")
df_ball = pd.read_csv("object_data_pp_P1_original.csv")


# %%
df_player["time"] = df_player["time"].apply(lambda x: x[0:23]+"+0100")
df_ball["time"] = df_ball["time"].apply(lambda x: x[:23]+"+0100")


# %%
df_player.head()

# %%
df_ball.head()

# %%
df_player.to_csv("player_data_pp_P1.csv")
df_player.to_csv("object_data_pp_P1.csv")

# %%
