package com.buddy.pm.myapplication.database;

import android.content.ContentValues;
import android.content.Context;
import android.database.DatabaseUtils;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import com.buddy.pm.myapplication.DataItem;

/**
 * Created by pm on 12/2/2017.
 */

public class DataSource {
    private Context mContext;
    SQLiteDatabase mDatabase;
    SQLiteOpenHelper mDbHelper;
    public DataSource(Context context){
        this.mContext=context;
        mDbHelper= new DBHelper((mContext));
        mDatabase=mDbHelper.getWritableDatabase();

    }
    public void open(){
        mDatabase=mDbHelper.getWritableDatabase();
    }
    public void close(){
        mDbHelper.close();
    }
    public DataItem createItem(DataItem item){
        ContentValues values= item.toValues();
        mDatabase.insert(ItemsTable.TABLE_ITEMS, null, values);
        return item;
    }
    public long getDataItemsCount(){
        return DatabaseUtils.queryNumEntries(mDatabase,ItemsTable.TABLE_ITEMS);
    }

}
