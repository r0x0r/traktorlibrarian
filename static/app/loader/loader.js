'use strict';

angular.module('librarian')
    .directive('loader', function () {

        return {
            scope: {
                message: '='
            },
            restrict: 'E',
            templateUrl: '/static/app/loader/loader.html',
            link: function($scope) {
                console.log($scope.message);
            }

        }
    });