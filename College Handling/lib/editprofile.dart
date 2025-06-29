

import 'dart:io';

import 'package:http/http.dart' as http;
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:image_picker/image_picker.dart ';

import 'package:permission_handler/permission_handler.dart';
import 'package:studybuddy/view%20profile.dart';


void main() {
  runApp(const EditProfile());
}

class EditProfile extends StatelessWidget {
  const EditProfile({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Edit Profile',
      theme: ThemeData(

        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const EditProfilePage(title: 'Edit Profile'),
    );
  }
}

class EditProfilePage extends StatefulWidget {
  const EditProfilePage({super.key, required this.title});

  final String title;

  @override
  State<EditProfilePage> createState() => _EditProfilePageState();
}

class _EditProfilePageState extends State<EditProfilePage> {

  _EditProfilePageState()
  {
    _get_data();
  }

  String gender = "Male";
  String photos = "photos";

  TextEditingController nameController= new TextEditingController();
  TextEditingController dobController= new TextEditingController();
  TextEditingController semesterController= new TextEditingController();
  TextEditingController guardian_nameController= new TextEditingController();
  TextEditingController guardian_realationController= new TextEditingController();
  TextEditingController addresController= new TextEditingController();
  TextEditingController phone_numberController= new TextEditingController();
  TextEditingController emailController= new TextEditingController();
  TextEditingController courseController= new TextEditingController();


  void _get_data() async{



    SharedPreferences sh = await SharedPreferences.getInstance();
    String url = sh.getString('url').toString();
    String img_url = sh.getString('imageurl').toString();
    String lid = sh.getString('lid').toString();

    final urls = Uri.parse('$url/student_profile/');
    try {
      final response = await http.post(urls, body: {
        'lid':lid



      });
      if (response.statusCode == 200) {
        String status = jsonDecode(response.body)['status'];
        if (status=='ok') {
          String name=jsonDecode(response.body)['name'].toString();
          String dob=jsonDecode(response.body)['dob'].toString();
          String genders=jsonDecode(response.body)['gender'].toString();
          String email=jsonDecode(response.body)['email'].toString();
          String phone=jsonDecode(response.body)['phone'].toString();
          String address=jsonDecode(response.body)['address'].toString();
          String semester=jsonDecode(response.body)['semester'].toString();
          String course=jsonDecode(response.body)['course'].toString();
          String gurdian_name=jsonDecode(response.body)['gurdian_name'].toString();
          String photo=img_url+jsonDecode(response.body)['photo'].toString();
          String gurdian_relation=jsonDecode(response.body)['gurdian_relation'].toString();
          print(photo);
          setState(() {

            nameController.text= name;
            dobController.text= dob;
            gender= genders;
            emailController.text= email;
            phone_numberController.text= phone;
            addresController.text= address;
            semesterController.text= semester;
            courseController.text= course;
            guardian_nameController.text= gurdian_name;
            photos= photo;
            guardian_realationController.text= gurdian_relation;
          });





        }else {
          Fluttertoast.showToast(msg: 'Not Found');
        }
      }
      else {
        Fluttertoast.showToast(msg: 'Network Error');
      }
    }
    catch (e){
      Fluttertoast.showToast(msg: e.toString());
    }
  }


@override
  Widget build(BuildContext context) {




    return WillPopScope(
      onWillPop: () async{ return true; },
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
          title: Text(widget.title),
        ),
        body: SingleChildScrollView(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[

              if (_selectedImage != null) ...{
                InkWell(
                  child:
                  Image.file(_selectedImage!, height: 400,),
                  radius: 399,
                  onTap: _checkPermissionAndChooseImage,
                  // borderRadius: BorderRadius.all(Radius.circular(200)),
                ),
              } else ...{
                // Image(image: NetworkImage(),height: 100, width: 70,fit: BoxFit.cover,),
                InkWell(
                  onTap: _checkPermissionAndChooseImage,
                  child:Column(
                    children: [
                      Image(image: NetworkImage('https://cdn.pixabay.com/photo/2017/11/10/05/24/select-2935439_1280.png'),height: 200,width: 200,),
                      Text('Select Image',style: TextStyle(color: Colors.cyan))
                    ],
                  ),
                ),
              },

              Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: nameController,
                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("Name")),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: dobController,
                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("DoB")),
                ),
              ),
              RadioListTile(value: "Male", groupValue: gender, onChanged: (value) { setState(() {gender="Male";}); },title: Text("Male"),),
              RadioListTile(value: "Female", groupValue: gender, onChanged: (value) { setState(() {gender="Female";}); },title: Text("Female"),),
              RadioListTile(value: "Other", groupValue: gender, onChanged: (value) { setState(() {gender="Other";}); },title: Text("Other"),),
              Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: emailController,
                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("Email")),
                ),
              ),   Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: phone_numberController,
                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("Phone")),
                ),
              ),   Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: addresController,
                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("address")),
                ),
              ),   Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: semesterController,
                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("semester")),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: courseController,
                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("course")),
                ),
              ),       Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: guardian_realationController,
                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("guardian relation")),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: guardian_nameController,
                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("guardian name")),
                ),
              ),

              ElevatedButton(
                onPressed: () {
                  _send_data();

                },
                child: Text("Confirm Edit"),
              ),
            ],
          ),
        ),
      ),
    );
  }
  void _send_data() async{





    String uname=nameController.text;
    String dob=dobController.text;
    String email=emailController.text;
    String phone=phone_numberController.text;
    String addr=addresController.text;
    String cour=courseController.text;
    String sem=semesterController.text;
    String gname=guardian_nameController.text;
    String gnamer=guardian_realationController.text;


    SharedPreferences sh = await SharedPreferences.getInstance();
    String url = sh.getString('url').toString();
    String lid = sh.getString('lid').toString();

    final urls = Uri.parse('$url/student_edit_profile/');
    try {

      final response = await http.post(urls, body: {
        "photo":photo,
        'name':uname,
        'dob':dob,
        'gender':gender,
        'email':email,
        'phone':phone,
        'addres':addr,
        'course':cour,
        'semester':sem,
        'guardian_name':gname,
        'guardian_realation':gnamer,
        'lid':lid,

      });
      if (response.statusCode == 200) {
        String status = jsonDecode(response.body)['status'];
        if (status=='ok') {

          Fluttertoast.showToast(msg: 'Updated Successfully');
          Navigator.push(context, MaterialPageRoute(
            builder: (context) => ViewProfilePage(title: "Profile"),));
        }else {
          Fluttertoast.showToast(msg: 'Not Found');
        }
      }
      else {
        Fluttertoast.showToast(msg: 'Network Error');
      }
    }
    catch (e){
      Fluttertoast.showToast(msg: e.toString());
    }
  }
  File? _selectedImage;
  String? _encodedImage;
  Future<void> _chooseAndUploadImage() async {
    final picker = ImagePicker();
    final pickedImage = await picker.pickImage(source: ImageSource.gallery);

    if (pickedImage != null) {
      setState(() {
        _selectedImage = File(pickedImage.path);
        _encodedImage = base64Encode(_selectedImage!.readAsBytesSync());
        photo = _encodedImage.toString();
      });
    }
  }

  Future<void> _checkPermissionAndChooseImage() async {
    final PermissionStatus status = await Permission.mediaLibrary.request();
    if (status.isGranted) {
      _chooseAndUploadImage();
    } else {
      showDialog(
        context: context,
        builder: (BuildContext context) => AlertDialog(
          title: const Text('Permission Denied'),
          content: const Text(
            'Please go to app settings and grant permission to choose an image.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    }
  }

  String photo = '';

}

