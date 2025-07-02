import React from 'react';
import { Store } from 'react-notifications-component';

export function Notification(title = '',message = '',type = 'danger',duration = 5000){
    return(
        <>
        {Store.addNotification({
            title: title,
            message: message,
            type: type,
            insert: "top",
            container: "top-right",
            animationIn: ["animate__animated", "animate__fadeIn"],
            animationOut: ["animate__animated", "animate__fadeOut"],
            dismiss: {
              duration: duration,
              onScreen: true
            }
        })}
        </>
    )
}