package com.buddy.pm.myapplication;

import android.content.ContentValues;

import com.buddy.pm.myapplication.database.ItemsTable;

/**
 * Created by pm on 12/2/2017.
 */

public class DataItem {
    private int itemId;
    private String User;
    private String message;
    private String category;
    private int sortPosition;
    private String image;

    public DataItem() {
    }

    public DataItem(int itemId, String user, String message, String category, int sortPosition, String image) {
        this.itemId = itemId;
        User = user;
        this.message = message;
        this.category = category;
        this.sortPosition = sortPosition;
        this.image = image;
    }

    public int getItemId() {
        return itemId;
    }

    public void setItemId(int itemId) {
        this.itemId = itemId;
    }

    public String getUser() {
        return User;
    }

    public void setUser(String user) {
        User = user;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public int getSortPosition() {
        return sortPosition;
    }

    public void setSortPosition(int sortPosition) {
        this.sortPosition = sortPosition;
    }

    public String getImage() {
        return image;
    }

    public void setImage(String image) {
        this.image = image;
    }

    @Override
    public String toString() {
        return "DataItem{" +
                "itemId=" + itemId +
                ", User='" + User + '\'' +
                ", message='" + message + '\'' +
                ", category='" + category + '\'' +
                ", sortPosition=" + sortPosition +
                ", image='" + image + '\'' +
                '}';
    }

    public ContentValues toValues(){
        ContentValues values= new ContentValues(6);
        values.put(ItemsTable.COLUMN_ID, itemId);
        values.put(ItemsTable.COLUMN_NAME, User);
        values.put(ItemsTable.COLUMN_DESCRIPTION, message);
        values.put(ItemsTable.COLUMN_CATEGORY, category);
        values.put(ItemsTable.COLUMN_POSITION, sortPosition);
        values.put(ItemsTable.COLUMN_IMAGE, image);
        return values;
    }
}

