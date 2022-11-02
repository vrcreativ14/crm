import { Store } from 'react-notifications-component'

export const Notifications = (title,message,type) => {
    return(
        Store.addNotification({
            title: title+"!",
            message: message,
            type: type,
            insert: "top",
            container: "top-right",
            animationIn: ["animate__animated", "animate__fadeIn"],
            animationOut: ["animate__animated", "animate__fadeOut"],
            dismiss: {
            duration: 6000,
            onScreen: true,
            showIcon: true
            }
        })
    )
}