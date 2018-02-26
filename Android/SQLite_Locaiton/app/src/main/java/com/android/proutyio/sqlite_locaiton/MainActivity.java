package com.android.proutyio.sqlite_locaiton;

import android.Manifest;
import android.content.ContentValues;
import android.content.Context;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.location.Location;
import android.provider.BaseColumns;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.SimpleCursorAdapter;
import android.widget.TextView;
import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.common.GoogleApiAvailability;
import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.location.LocationListener;



public class MainActivity extends AppCompatActivity implements GoogleApiClient.ConnectionCallbacks, GoogleApiClient.OnConnectionFailedListener
{
    private SQLite sqlite;
    private Button submit_button;
    private Cursor cursor;
    private SimpleCursorAdapter adapter;
    private SQLiteDatabase db;
    private GoogleApiClient gclient;
    private LocationRequest locationrequest;
    private Location lastlocation;
    private LocationListener locationlistener;
    private static final int LOCATION_PERMISSION_RESULT = 17;
    private String[] data = new String[2];

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if(gclient == null) {
            gclient = new GoogleApiClient.Builder(this)
                    .addConnectionCallbacks(this)
                    .addOnConnectionFailedListener(this)
                    .addApi(LocationServices.API)
                    .build();
        }
        locationrequest = LocationRequest.create();
        locationrequest.setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY);
        locationrequest.setInterval(50);
        locationrequest.setFastestInterval(50);
        locationlistener = new LocationListener() {
            @Override
            public void onLocationChanged(Location location) {}
        };


        sqlite = new SQLite(this);
        db = sqlite.getWritableDatabase();

        submit_button = (Button) findViewById(R.id.submit_button);
        submit_button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                data = getLocation();
                insertDB(db, data);
            }
        });
        populateTable();
    }


    private void insertDB(SQLiteDatabase db, String[] data){
        if (data[0] == null){
            data[0] = "-123.2";
            data[1] = "44.5";
        }
        if (db != null) {
            ContentValues contentvalues = new ContentValues();
            contentvalues.put(DBContract.DemoTable.COLUMN_NAME_DEMO_STRING, ((EditText) findViewById(R.id.string_input)).getText().toString());
            contentvalues.put(DBContract.DemoTable.COLUMN_NAME_DEMO_LONG, data[0]);
            contentvalues.put(DBContract.DemoTable.COLUMN_NAME_DEMO_LAT, data[1]);
            db.insert(DBContract.DemoTable.TABLE_NAME, null, contentvalues);
            populateTable();
        } else
            Log.d("LOG", "Error could not write to database");
    }



    private String[] getLocation(){
        String[] s = new String[2];
        if(ActivityCompat.checkSelfPermission(this,Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED &&
                ActivityCompat.checkSelfPermission(this,Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED){

            ActivityCompat.requestPermissions(this, new String[]{android.Manifest.permission.ACCESS_FINE_LOCATION,android.Manifest.permission.ACCESS_COARSE_LOCATION},
                    LOCATION_PERMISSION_RESULT);
            return s;
        }
        else{
            LocationServices.FusedLocationApi.requestLocationUpdates(gclient,locationrequest,locationlistener);
            lastlocation = LocationServices.FusedLocationApi.getLastLocation(gclient);
            if(lastlocation != null)
                s[0] = String.valueOf(lastlocation.getLongitude());
                s[1] = String.valueOf(lastlocation.getLatitude());
                return s;
        }
    }


    @Override
    protected void onStart() {
        gclient.connect();
        super.onStart();
    }


    @Override
    protected void onStop() {
        gclient.disconnect();
        super.onStop();
    }


    @Override
    public void onConnected(@Nullable Bundle bundle) {
        if(ActivityCompat.checkSelfPermission(this,Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED &&
                ActivityCompat.checkSelfPermission(this,Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED){

            ActivityCompat.requestPermissions(this, new String[]{android.Manifest.permission.ACCESS_FINE_LOCATION,android.Manifest.permission.ACCESS_COARSE_LOCATION},
                                                    LOCATION_PERMISSION_RESULT);
           return;
        }
        updateLocation();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults){
        if(requestCode == LOCATION_PERMISSION_RESULT)
            if(grantResults.length > 0)
                updateLocation();

    }

    private void updateLocation() {
        if( (ActivityCompat.checkSelfPermission(this,Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED)
                && (ActivityCompat.checkSelfPermission(this,Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED)){
            return;
        }
        lastlocation = LocationServices.FusedLocationApi.getLastLocation(gclient);
        if(lastlocation != null) {}
        else {
            LocationServices.FusedLocationApi.requestLocationUpdates(gclient,locationrequest,locationlistener);
        }
    }

    @Override
    public void onConnectionSuspended(int i) {}

    @Override
    public void onConnectionFailed(@NonNull ConnectionResult connectionResult) {}

    private void populateTable()
    {
        if(db != null) {
            if(adapter != null && adapter.getCursor() != null)
                if(!adapter.getCursor().isClosed())
                    adapter.getCursor().close();

            cursor = db.query(DBContract.DemoTable.TABLE_NAME,
                    new String[]{DBContract.DemoTable._ID,
                            DBContract.DemoTable.COLUMN_NAME_DEMO_STRING,
                            DBContract.DemoTable.COLUMN_NAME_DEMO_LONG,
                            DBContract.DemoTable.COLUMN_NAME_DEMO_LAT},
                    null,null,null,null,null);
            ListView listview = (ListView) findViewById(R.id.listview);
            adapter = new SimpleCursorAdapter(this, R.layout.sql_list_item, cursor,
                    new String[]{DBContract.DemoTable.COLUMN_NAME_DEMO_STRING,
                            DBContract.DemoTable.COLUMN_NAME_DEMO_LONG,
                            DBContract.DemoTable.COLUMN_NAME_DEMO_LAT},
                    new int[]{R.id.listview_string, R.id.listview_long, R.id.listview_lat}, 0);
            listview.setAdapter(adapter);
        }
    }


    final class DBContract
    {
        private DBContract(){};
        public final class DemoTable implements BaseColumns {
            public static final String DB_NAME = "demo_db";
            public static final String TABLE_NAME = "demo";
            public static final String COLUMN_NAME_DEMO_STRING = "demo_string";
            public static final String COLUMN_NAME_DEMO_LONG = "demo_long";
            public static final String COLUMN_NAME_DEMO_LAT = "demo_lat";
            public static final int DB_VERSION = 1;

            public static final String SQL_CREATE_DEMO_TABLE = "CREATE TABLE " +
                    DemoTable.TABLE_NAME + "(" + DemoTable._ID + " INTEGER PRIMARY KEY NOT NULL," +
                    DemoTable.COLUMN_NAME_DEMO_STRING + " VARCHAR(255)," +
                    DemoTable.COLUMN_NAME_DEMO_LONG + " INTEGER," +
                    DemoTable.COLUMN_NAME_DEMO_LAT + " INTEGER);";

            public  static final String SQL_DROP_DEMO_TABLE = "DROP TABLE IF EXISTS " + DemoTable.TABLE_NAME;
        }
    }



    class SQLite extends SQLiteOpenHelper {
        public SQLite(Context context) {
            super(context, DBContract.DemoTable.DB_NAME, null, DBContract.DemoTable.DB_VERSION);
        }

        @Override
        public void onCreate(SQLiteDatabase db) {
            db.execSQL(DBContract.DemoTable.SQL_CREATE_DEMO_TABLE);

            ContentValues testValues = new ContentValues();
            testValues.put(DBContract.DemoTable.COLUMN_NAME_DEMO_LONG, 142);
            testValues.put(DBContract.DemoTable.COLUMN_NAME_DEMO_LAT, 42);
            testValues.put(DBContract.DemoTable.COLUMN_NAME_DEMO_STRING, "create");
            db.insert(DBContract.DemoTable.TABLE_NAME, null, testValues);
        }

        @Override
        public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
            db.execSQL(DBContract.DemoTable.SQL_DROP_DEMO_TABLE);
            onCreate(db);
        }
    }

}
