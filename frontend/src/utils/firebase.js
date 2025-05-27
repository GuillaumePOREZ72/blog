// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAqI5CTVri3ynQvXAGQy53tSbmtBtHtB3k",
  authDomain: "guiguiblog-ee4d7.firebaseapp.com",
  projectId: "guiguiblog-ee4d7",
  storageBucket: "guiguiblog-ee4d7.firebasestorage.app",
  messagingSenderId: "771074592920",
  appId: "1:771074592920:web:a763c88e8e38693105c0ed",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const storage = storage(app);

const uploadFileAsync = async (folder, files, formatName, maxFilesSize) => {
  return Promise((resolve, reject) => {
    if (files.size > maxFilesSize * 1024 * 1024) {
      reject(new Error("File size is too large"));
      return;
    }

    const storageRef = ref(storage, `/${folder + formatName}`);
    const uploadTask = UploadBytesResumable(storageRef, files);

    uploadTask.on(
      "state_changed",
      (snapshot) => {
        const progress = Math.round(
          (snapshot.bytesTransferred / snapshot.totalBytes) * 100
        );
        switch (snapshot.state) {
          case "paused":
            console.log("Upload is paused");
            break;
          case "running":
            console.log("Upload is running");
            break;
        }
      },
      (error) => {
        reject(error);
      },
      () => {
        getDownloadURL(uploadTask.snapshot.ref).then((downloadURL) => {
          resolve(downloadURL);
        });
      }
    );
  });

};

const firebase = {
  uploadFileAsync,
}

export default firebase;
