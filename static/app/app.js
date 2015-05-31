angular.module('librarian', ['ngRoute'])

.config(['$routeProvider', '$locationProvider',
        function($routeProvider, $locationProvider, $http)  {

    $routeProvider
        .when('/clean/', {
            templateUrl: '../static/app/clean/clean.html',
            controller: 'CleanController'
        })
        .when('/export', {
            templateUrl: '../static/app/export/export.html',
            controller: 'ExportController'
        })
        .when('/', {
            templateUrl: '../static/app/landing/landing.html',
            controller: 'LandingController'
        });
        }]);
