import 'dart:io';

import 'package:http/http.dart' as http;
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:image_picker/image_picker.dart ';

import 'package:permission_handler/permission_handler.dart';
import 'login.dart';


void main() {
  runApp(const MyMySignup());
}

class MyMySignup extends StatelessWidget {
  const MyMySignup({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MySignup',
      theme: ThemeData(

        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyMySignupPage(title: 'MySignup'),
    );
  }
}

class MyMySignupPage extends StatefulWidget {
  const MyMySignupPage({super.key, required this.title});

  final String title;

  @override
  State<MyMySignupPage> createState() => _MyMySignupPageState();
}

class _MyMySignupPageState extends State<MyMySignupPage> {
  _MyMySignupPageState(){
    getdata();
  }
  String gender = "Male";
  File? uploadimage;
  TextEditingController nameController= new TextEditingController();
  TextEditingController dobController= new TextEditingController();
  TextEditingController semesterController= new TextEditingController();
  TextEditingController guardian_nameController= new TextEditingController();
  TextEditingController guardian_realationController= new TextEditingController();
  TextEditingController addresController= new TextEditingController();
  TextEditingController phone_numberController= new TextEditingController();
  TextEditingController emailController= new TextEditingController();
  TextEditingController courseController= new TextEditingController();
  TextEditingController passwoardController= new TextEditingController();
  TextEditingController comfirmpasswoardController= new TextEditingController();

  List<int> election_id_ = <int>[];
  List<String> election_name_ = <String>[];
  TextEditingController subdatecontroller=new TextEditingController();
  String dropdownValue1 ="";





  // Future<void> chooseImage() async {
  //   // final choosedimage = await ImagePicker().pickImage(source: ImageSource.gallery);
  //   //set source: ImageSource.camera to get image from camera
  //   setState(() {
  //     // uploadimage = File(choosedimage!.path);
  //   });
  // }




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
              ),

              Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: guardian_nameController,

                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("guardian name")),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: guardian_realationController,

                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("guardian relation")),
                ),
              ),
              Container(
                decoration: BoxDecoration(
                  color: Colors.grey,
                  border: Border.all(color: Colors.black12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(

                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text('Course:         ',
                      style: TextStyle(
                        fontSize: 15.0,
                        fontWeight: FontWeight.bold,
                        color: Colors.black,
                      ),),
                    DropdownButton<String>(
                      // isExpanded: true,
                      value: dropdownValue1,
                      onChanged: (String? value) {

                        print(dropdownValue1);
                        print("Hiiii");
                        setState(() {
                          dropdownValue1 = value!;
                        });
                      },
                      items: election_name_.map((String value) {
                        return DropdownMenuItem(

                          value: value,
                          child: Text(value,
                            style: TextStyle(
                              fontSize: 15.0,
                              fontWeight: FontWeight.bold,
                              color: Colors.black,
                              // backgroundColor: Colors.brown,
                            ),),
                        );
                      }).toList(),
                    ),

                  ],
                ),
              ),  Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: semesterController,

                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("semester")),
                ),
              ),  Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: passwoardController,

                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("passwoard")),
                ),
              ),  Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: comfirmpasswoardController,

                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("comfirm passwoard")),
                ),
              ),
              //
              //
              // Padding(
              //   padding: const EdgeInsets.all(8),
              //   child: TextField(
              //
              //     decoration: InputDecoration(border: OutlineInputBorder(),label: Text("Password")),
              //   ),
              // ),     Padding(
              //   padding: const EdgeInsets.all(8),
              //   child: TextField(
              //
              //     decoration: InputDecoration(border: OutlineInputBorder(),label: Text("Confirm Password")),
              //   ),
              // ),

              ElevatedButton(
                onPressed: () {

                  _send_data() ;

                },
                child: Text("Signup"),
              ),TextButton(
                onPressed: () {},
                child: Text("Login"),
              ),
            ],
          ),
        ),
      ),
    );
  }
  void getdata() async{
    List<int> election_id = <int>[];
    List<String> election_name = <String>[];


    SharedPreferences sh = await SharedPreferences.getInstance();
    String url = sh.getString('url').toString();
    final urls = Uri.parse('$url/studentviewcourse/');


    var data = await http.post(urls, body: {});
    var jsondata = json.decode(data.body);
    String status = jsondata['status'];

    var arr = jsondata["data"];


    for (int i = 0; i < arr.length; i++) {
      election_id.add(arr[i]['id']);
      election_name.add(arr[i]['course_name']);
    }
    setState(() {
      election_id_ = election_id;
      election_name_ = election_name;
      dropdownValue1= election_name_.first;
    });
  }

  void _send_data() async{

    String uname=nameController.text;
    String dob=dobController.text;
    String gur=guardian_realationController.text;
    String sem=semesterController.text;
    String nam=guardian_nameController.text;
    String cour=courseController.text;
    String addr=addresController.text;
    String num=phone_numberController.text;
    String mail= emailController.text;
    String pas= passwoardController.text;
    String pass= comfirmpasswoardController.text;



    SharedPreferences sh = await SharedPreferences.getInstance();
    String url = sh.getString('url').toString();

    final urls = Uri.parse('$url/student_signup/');
    try {

      final response = await http.post(urls, body: {
        "photo":photo,
        'gender':gender,
        'name':uname,
        'semester':sem,
        'guardian_name':nam,
        'guardian_realation':gur,
        'course':election_id_[ election_name_.indexOf(dropdownValue1)].toString(),
        'addres':addr,
        'phone_number':num,
        'email':mail,
        'passwoard':pas,
        'comfirmpasswoard':pass ,
        'dob':dob ,



      });
      if (response.statusCode == 200) {
        String status = jsonDecode(response.body)['status'];
        if (status=='ok') {

          Fluttertoast.showToast(msg: 'Registration Successfull');
          Navigator.push(context, MaterialPageRoute(
            builder: (context) => MyLoginPage(title: "Login"),));
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