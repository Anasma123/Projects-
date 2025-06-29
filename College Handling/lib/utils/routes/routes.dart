import 'package:flutter/material.dart';
import 'package:studybuddy/pages/detail/detail_screen.dart';
import 'package:studybuddy/pages/home/home_screen.dart';
import 'package:studybuddy/pages/login/login_screen.dart';
import 'package:studybuddy/pages/order/order_completed_scren.dart';
import 'package:studybuddy/pages/splash_screen.dart';


class Routes {
  Routes._();

  //static variables
  static const String splash = '/splash';
  static const String login = '/login';
  static const String home = '/home';
  static const String order = '/order';
  static const String detail = '/detail';

  //static const String home = '/home';
  //static const String detail = '/detail';

  static final routes = <String, WidgetBuilder>{
    splash: (BuildContext context) => const SplashScreen(),
    login: (BuildContext context) => const LoginScreen(),
    home: (BuildContext context) => const HomeScreen(),
    detail: (BuildContext context) => const DetailScreen(),
    order: (BuildContext context) => const OrderCompletedScreen(),

    // home: (BuildContext context) => HomeScreen(),
    //detail: (BuildContext context) => DetailScreen(),
  };
}
