/**
 * Autor: Víctor Morant
 * Fecha: 15/11/2025
 * Descripción:
     Activity para gestionar las notificaciones del servicio de escaneo de beacons.
     Incluye creación, actualización y cancelación de notificaciones.
 */

package com.example.eolos.servicio;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

import androidx.core.app.NotificationCompat;

public class NotificationHelper {

    public static final String CHANNEL_ID = PermisosHelper.CHANNEL_ID;

    public static void createChannel(Context ctx) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager nm = (NotificationManager) ctx.getSystemService(Context.NOTIFICATION_SERVICE);
            if (nm.getNotificationChannel(CHANNEL_ID) == null) {
                NotificationChannel ch = new NotificationChannel(CHANNEL_ID, "Escaneo de Beacons", NotificationManager.IMPORTANCE_LOW);
                ch.setDescription("Notificaciones relacionadas con el escaneo y envío de datos");
                nm.createNotificationChannel(ch);
            }
        }
    }

    // Notificación sin acción (es la anterior pero la conservamos por si acaso)
    public static Notification buildForegroundNotification(Context ctx, String title, String text, PendingIntent contentIntent) {
        createChannel(ctx);

        return new NotificationCompat.Builder(ctx, CHANNEL_ID)
                .setContentTitle(title)
                .setContentText(text)
                .setSmallIcon(android.R.drawable.stat_sys_data_bluetooth)
                .setContentIntent(contentIntent)
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .setPriority(NotificationCompat.PRIORITY_LOW)
                .build();
    }

    // Notificación CON acción "Detener"
    public static Notification buildForegroundNotificationWithStopAction(Context ctx, String title, String text, PendingIntent contentIntent, PendingIntent stopIntent) {
        createChannel(ctx);

        return new NotificationCompat.Builder(ctx, CHANNEL_ID)
                .setContentTitle(title)
                .setContentText(text)
                .setSmallIcon(android.R.drawable.stat_sys_data_bluetooth)
                .setContentIntent(contentIntent)
                .addAction(android.R.drawable.ic_media_pause, "Detener", stopIntent)  // Acción "Detener"
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .setPriority(NotificationCompat.PRIORITY_LOW)
                .build();
    }

    // Actualiza una notificación existente (mismo id)
    public static void updateNotification(Context ctx, int notifId, String title, String text) {
        NotificationManager nm = (NotificationManager) ctx.getSystemService(Context.NOTIFICATION_SERVICE);
        Notification n = new NotificationCompat.Builder(ctx, CHANNEL_ID)
                .setContentTitle(title)
                .setContentText(text)
                .setSmallIcon(android.R.drawable.stat_sys_data_bluetooth)
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .setPriority(NotificationCompat.PRIORITY_LOW)
                .build();
        nm.notify(notifId, n);
    }

    // Cancelar notificación por id
    public static void cancel(Context ctx, int notifId) {
        NotificationManager nm = (NotificationManager) ctx.getSystemService(Context.NOTIFICATION_SERVICE);
        nm.cancel(notifId);
    }
}