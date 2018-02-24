package com.android.r00t.basicui;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button gview = (Button) findViewById(R.id.gview);
        gview.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(MainActivity.this,GridViewActivity.class);
                startActivity(intent);
            }
        });

        Button hview = (Button) findViewById(R.id.hview);
        hview.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(MainActivity.this,HorizontalViewActivity.class);
                startActivity(intent);
            }
        });

        Button vview = (Button) findViewById(R.id.vview);
        vview.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(MainActivity.this,VerticalViewActivity.class);
                startActivity(intent);
            }
        });

        Button rview = (Button) findViewById(R.id.rview);
        rview.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(MainActivity.this,RelativeViewActivity.class);
                startActivity(intent);
            }
        });
    }
}
