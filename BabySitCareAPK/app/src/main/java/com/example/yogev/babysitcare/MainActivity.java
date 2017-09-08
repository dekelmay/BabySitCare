package com.example.yogev.babysitcare;

import android.annotation.TargetApi;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.TaskStackBuilder;
import android.content.Context;
import android.content.Intent;
import android.database.CharArrayBuffer;
import android.graphics.Color;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;


import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.Scanner;
import java.util.Timer;

import android.support.v7.app.NotificationCompat;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends AppCompatActivity {

    Button Start;
    NotificationCompat.Builder notification;
    PendingIntent pIntent;
    NotificationManager manager;
    Intent resultIntent;
    TaskStackBuilder stackBuilder;
    BufferedReader input;

    String msg ="";
    Boolean childFlag = false;



    private Socket socket;

    private static final int SERVERPORT = 9999;
    protected static String SERVER_IP = "";
    protected static boolean setServerIP = false;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button scan;

        scan = (Button) findViewById(R.id.scan);


        scan.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent rIntent = new Intent(MainActivity.this, ReaderActivity.class);
                startActivity(rIntent);
            }
        });

        new Thread(new ClientThread()).start();


    }




    public void onClick(View view) {
        try {
            Toast.makeText(MainActivity.this, "LED on", Toast.LENGTH_SHORT).show();
            String str = "led";
            PrintWriter out = new PrintWriter(new BufferedWriter(
                    new OutputStreamWriter(socket.getOutputStream())),
                    true);
            out.println(str);
        } catch (UnknownHostException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void onClickMotor(View view) {
        try {
            Toast.makeText(MainActivity.this, "Car window opened", Toast.LENGTH_SHORT).show();
            String str = "Motor";
            PrintWriter out = new PrintWriter(new BufferedWriter(
                    new OutputStreamWriter(socket.getOutputStream())),
                    true);
            out.println(str);
        } catch (UnknownHostException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void onClickCloseWindow(View view) {


        try {

            String str = "closeWindow";
            PrintWriter out = new PrintWriter(new BufferedWriter(
                    new OutputStreamWriter(socket.getOutputStream())),
                    true);
            out.println(str);


        } catch (UnknownHostException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void onClickNotification(View view) {

        startNotification("test");

    }


    class ClientThread implements Runnable {

        @Override
        public void run() {

            try {

                while(!setServerIP){

                }

                InetAddress serverAddr = InetAddress.getByName(SERVER_IP);

                socket = new Socket(serverAddr, SERVERPORT);

                input = new BufferedReader(new InputStreamReader(socket.getInputStream() ));

                String msgFromClient="";
                Timer timer = new Timer();


                while(true){
                    msgFromClient = input.readLine().trim();

                    if(msgFromClient.compareTo("alert") == 0){ //activate alarm
                        startNotification("You forgot your child!");

                    }else if(msgFromClient.compareTo("windowOpened") == 0){
                        startNotification("Temp in car high window opened.");

                    }else if(msgFromClient.compareTo("windowUp") == 0){
                        startNotification("Car window closed.");
                    }



                    /*if (msg.compareTo(temp) != 0) //update message
                        msg = temp;*/



                }

            } catch (UnknownHostException e1) {
                e1.printStackTrace();
            } catch (IOException e1) {
                e1.printStackTrace();
            }

        }

    }



    @TargetApi(Build.VERSION_CODES.JELLY_BEAN)
    protected void startNotification(String msg) {
        // TODO Auto-generated method stub
        //Creating Notification Builder
        notification = new NotificationCompat.Builder(MainActivity.this);
        //Title for Notification
        notification.setContentTitle("Baby Sitcare");
        //Message in the Notification
        notification.setContentText(msg);
        //Alert shown when Notification is received
        notification.setTicker("Child alarm!");
        //Icon to be set on Notification
        notification.setSmallIcon(R.mipmap.ic_babycare);
        //notification sound
        Uri soundUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
        notification.setSound(soundUri);
        //notification Vibratation
        notification.setVibrate(new long[] { 1000, 1000});
        //notification LED == Red
        notification.setLights(Color.RED, 3000, 3000);
        //clear notification when pressed
        notification.setAutoCancel(true);

        //notification.setVisibility(NotificationCompat.VISIBILITY_PUBLIC);
        //Creating new Stack Builder
        stackBuilder = TaskStackBuilder.create(MainActivity.this);
        stackBuilder.addParentStack(Result.class);
        //Intent which is opened when notification is clicked
        resultIntent = new Intent(MainActivity.this, Result.class);
        stackBuilder.addNextIntent(resultIntent);
        pIntent =  stackBuilder.getPendingIntent(0, PendingIntent.FLAG_UPDATE_CURRENT);
        notification.setContentIntent(pIntent);
        manager =(NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        manager.notify(0, notification.build());


    }
}