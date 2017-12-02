package com.buddy.pm.myapplication;
import android.content.Intent;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteException;
import android.database.sqlite.SQLiteOpenHelper;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.buddy.pm.myapplication.database.DBHelper;
import com.buddy.pm.myapplication.database.DataSource;

import java.util.ArrayList;

import butterknife.BindView;
import butterknife.ButterKnife;
import butterknife.OnClick;

import static android.provider.AlarmClock.EXTRA_MESSAGE;

public class MainActivity extends AppCompatActivity {
    public static final String EXTRA_MESSAGE = "com.buddy.pm.myapplication.MESSAGE";
    public ArrayList<DataItem> dataItems= new ArrayList<DataItem>();
// 1 user has many properties
    DataSource mDataSource;
    public DataItem dataItem;
    public int id;
    public String user="Spongebob";
    public String description="";
    public String category="Assessment";
    public int sortPosition=0;
    public String image="";



    @BindView(R.id.sendButton)
    Button sendButton;

    @OnClick(R.id.sendButton)
    public void onClickButtonClick(){
        Intent intent = new Intent(this, DisplayMessageActivity.class);
        EditText editText = (EditText) findViewById(R.id.editText);
        String message = editText.getText().toString();
        description=message;
        dataItem= new DataItem(id,user,description,category,sortPosition,image);
        dataItems.add(dataItem);
        intent.putExtra(EXTRA_MESSAGE, dataItem.getItemId()+", "+ dataItem.getUser()+", "+dataItem.getMessage()+", "+dataItem.getCategory());
        startActivity(intent);
    }


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        ButterKnife.bind(this);

    }

//
////    /** Called when the user taps the Send button */
////    public void sendMessage(View view) {
//Intent intent = new Intent(this, DisplayMessageActivity.class);
//    EditText editText = (EditText) findViewById(R.id.editText);
//    String message = editText.getText().toString();
//    description=message;
//    dataItem= new DataItem(id,user,description,category,sortPosition,image);
//        dataItems.add(dataItem);
//        intent.putExtra(EXTRA_MESSAGE, dataItem.getItemId()+", "+ dataItem.getUser()+", "+dataItem.getMessage()+", "+dataItem.getCategory());
//    startActivity(intent);
////
////    }


}


