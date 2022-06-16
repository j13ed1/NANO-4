import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format


config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']=config['AWS_SECRET_ACCESS_KEY']


def create_spark_session():
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):

    # get filepath to song data file
    #loads the data from the S3 bucket, then performs ETL process for creating songs and artists tables 
    song_data = os.path.join(input_data,"song_data/*/*/*/*.json")

    # read song data file
    df = spark.read.json(song_data)
    
    
    # extract columns to create songs table
    songs_table = df.select("song_id","title","artist_id","year","duration").drop_duplicates()
    
      
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.partitionBy('year', 'artist_id').parquet(os.path.join(output_data, 'songs.parquet'), 'overwrite')
    print("--- songs.parquet completed ---")
             
    
    # extract columns to create artists table
    artists_table = df.select("artist_id","artist_name","artist_location","artist_latitude","artist_longitude").drop_duplicates()
    
   # write artists table to parquet files
    artists_table.write.parquet(output_data + "artists/", mode="overwrite")
    print("--- artists.parquet completed ---")
    print("*** process_song_data completed ***\n\n")


    def process_log_data(spark, input_data, output_data):
      
    # get filepath to log data file
    # Load data from log_data dataset and extract columns
    log_data =os.path.join(input_data,"log_data/*/*/*.json")

    # read log data file
    df = spark.read.json(log_data)
    
    # filter by actions for song plays
    #songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent
    songplays_table = df['ts', 'userId', 'level','sessionId', 'location', 'userAgent']
     df = df.filter(df.page == "NextSong")

    # extract columns for users table 
    #user_id, first_name, last_name, gender, level
    users_table = df.select("userId","firstName","lastName","gender","level").drop_duplicates()
    
    # write users table to parquet files
    users_table.write.parquet(os.path.join(output_data, "users/") , mode="overwrite")
    print("--- users.parquet completed ---")
    
   
    # create datetime column from original timestamp column
    get_datetime = udf(lambda x: str(datetime.fromtimestamp(int(x) / 1000)))
    actions_df = actions_df.withColumn('datetime', get_datetime(actions_df.ts))
 
    
    # extract columns to create time table
    time_table  = actions_df['start_time', 'hour', 'day', 'week', 'month', 'year', 'weekday']
    
    # write time table to parquet files partitioned by year and month
    time_table.write.partitionBy('year', 'month').parquet(os.path.join(output_data, 'time.parquet'), 'overwrite')
    print("--- time.parquet completed ---")
    
    
    # read in song data to use for songplays table
    song_df = spark.read.parquet("songs.parquet")

    # extract columns from joined song and log datasets to create songplays table 
    df = df.join(song_df, song_df.title == df.song)
    songplays_table = df['start_time', 'userId', 'level', 'song_id', 'artist_id', 'sessionId', 'location', 'userAgent']
    songplays_table.select(monotonically_increasing_id().alias('songplay_id')).collect()
    
    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.parquet(os.path.join(output_data, 'songplays.parquet'), 'overwrite')
    print("--- songplays.parquet completed ---")
    print("*** process_log_data completed ***\n\nEND")

    
def main():
    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
    output_data = ""
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
